# android_app/services/notification_service.py
from kivy.utils import platform
import requests
import threading
import time

if platform == 'android':
    from jnius import autoclass, PythonJavaClass, java_method
    
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    NotificationListenerService = autoclass('android.service.notification.NotificationListenerService')

class NotificationService:
    def __init__(self, config, log_callback):
        self.config = config
        self.log = log_callback
        self.running = False
        self.notification_queue = []
        self.thread = None
        
    def start(self):
        if platform != 'android':
            self.log('Notification monitoring only works on Android')
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._process_notifications, daemon=True)
        self.thread.start()
        self.log('Notification monitoring started')
        self.log('Note: Enable notification access in Settings for this app')
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        self.log('Notification monitoring stopped')
    
    def add_notification(self, notification_data):
        """Called when a new notification is received"""
        self.notification_queue.append(notification_data)
    
    def _process_notifications(self):
        """Process queued notifications"""
        while self.running:
            try:
                if self.notification_queue:
                    notification = self.notification_queue.pop(0)
                    self.send_notification(notification)
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                self.log(f'Error processing notifications: {str(e)}')
                time.sleep(5)
    
    def send_notification(self, notification_data):
        try:
            url = f"{self.config.get_server_url()}/notification"
            response = requests.post(
                url,
                json=notification_data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                app_name = notification_data.get('app_name', 'Unknown')
                self.log(f'Notification sent: {app_name}')
            else:
                self.log(f'Notification send failed: {response.status_code}')
                
        except requests.exceptions.RequestException as e:
            self.log(f'Network error sending notification: {str(e)}')
        except Exception as e:
            self.log(f'Error sending notification: {str(e)}')


# Note: To implement full notification listener, you need to create
# a custom NotificationListenerService in Java/Kotlin and integrate it
# with your Kivy app. This is a simplified version that shows the structure.
# For a complete implementation, you would need:
# 1. Create a NotificationListener class extending NotificationListenerService
# 2. Override onNotificationPosted() method
# 3. Register the service in AndroidManifest.xml
# 4. Request notification access permission from user

class SimpleNotificationMonitor:
    """
    This is a placeholder for notification monitoring.
    Full implementation requires Java/Kotlin code for NotificationListenerService.
    
    For testing purposes, you can manually trigger notifications:
    """
    
    def __init__(self, notification_service):
        self.service = notification_service
    
    def simulate_notification(self, app_name, title, text, package_name):
        """For testing - simulate a notification"""
        notification_data = {
            'device_id': self.service.config.get_device_id(),
            'app_name': app_name,
            'title': title,
            'text': text,
            'package_name': package_name,
            'timestamp': int(time.time() * 1000)
        }
        self.service.add_notification(notification_data)