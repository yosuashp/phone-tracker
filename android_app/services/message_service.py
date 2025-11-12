# android_app/services/message_service.py
from kivy.utils import platform
import requests
import threading
import time

if platform == 'android':
    from jnius import autoclass, cast
    
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Uri = autoclass('android.net.Uri')

class MessageService:
    def __init__(self, config, log_callback):
        self.config = config
        self.log = log_callback
        self.running = False
        self.last_message_time = 0
        self.thread = None
        
    def start(self):
        if platform != 'android':
            self.log('Message monitoring only works on Android')
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_messages, daemon=True)
        self.thread.start()
        self.log('Message monitoring started')
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        self.log('Message monitoring stopped')
    
    def _monitor_messages(self):
        """Monitor SMS messages periodically"""
        while self.running:
            try:
                messages = self._read_sms()
                for msg in messages:
                    if msg['timestamp'] > self.last_message_time:
                        self.send_message(msg)
                        self.last_message_time = msg['timestamp']
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.log(f'Error monitoring messages: {str(e)}')
                time.sleep(30)  # Wait longer on error
    
    def _read_sms(self):
        """Read SMS messages from Android"""
        try:
            activity = PythonActivity.mActivity
            context = activity.getApplicationContext()
            content_resolver = context.getContentResolver()
            
            # SMS URI
            uri = Uri.parse('content://sms/')
            
            # Query SMS
            cursor = content_resolver.query(
                uri,
                None,
                None,
                None,
                'date DESC'
            )
            
            messages = []
            if cursor and cursor.moveToFirst():
                count = 0
                while count < 50:  # Get last 50 messages
                    try:
                        address_idx = cursor.getColumnIndex('address')
                        body_idx = cursor.getColumnIndex('body')
                        date_idx = cursor.getColumnIndex('date')
                        type_idx = cursor.getColumnIndex('type')
                        read_idx = cursor.getColumnIndex('read')
                        
                        address = cursor.getString(address_idx) if address_idx >= 0 else None
                        body = cursor.getString(body_idx) if body_idx >= 0 else None
                        date = cursor.getLong(date_idx) if date_idx >= 0 else 0
                        msg_type = cursor.getInt(type_idx) if type_idx >= 0 else 0
                        read = cursor.getInt(read_idx) if read_idx >= 0 else 0
                        
                        # Type 1 = received, 2 = sent
                        message_type = 'received' if msg_type == 1 else 'sent'
                        
                        messages.append({
                            'device_id': self.config.get_device_id(),
                            'sender': address if msg_type == 1 else 'me',
                            'recipient': 'me' if msg_type == 1 else address,
                            'message_body': body,
                            'message_type': message_type,
                            'timestamp': date,
                            'read_status': read == 1
                        })
                        
                    except Exception as e:
                        self.log(f'Error reading SMS row: {str(e)}')
                    
                    if not cursor.moveToNext():
                        break
                    count += 1
            
            if cursor:
                cursor.close()
            
            return messages
            
        except Exception as e:
            self.log(f'Error reading SMS: {str(e)}')
            return []
    
    def send_message(self, message_data):
        try:
            url = f"{self.config.get_server_url()}/message"
            response = requests.post(
                url,
                json=message_data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                sender = message_data.get('sender', 'Unknown')
                self.log(f'Message sent: from {sender}')
            else:
                self.log(f'Message send failed: {response.status_code}')
                
        except requests.exceptions.RequestException as e:
            self.log(f'Network error sending message: {str(e)}')
        except Exception as e:
            self.log(f'Error sending message: {str(e)}')