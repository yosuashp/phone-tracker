# android_app/main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.utils import platform
from services.location_service import LocationService
from services.device_service import DeviceService
from services.message_service import MessageService
from services.notification_service import NotificationService
from utils.config import Config
from utils.storage import Storage
import threading

class PhoneTrackerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config = Config()
        self.storage = Storage()
        self.running = False
        
        # Services
        self.location_service = None
        self.device_service = None
        self.message_service = None
        self.notification_service = None
        
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(
            text='Phone Tracker Service',
            size_hint=(1, 0.1),
            font_size='20sp',
            bold=True
        )
        self.layout.add_widget(title)
        
        # Server URL input
        url_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        url_layout.add_widget(Label(text='Server URL:', size_hint=(0.3, 1)))
        self.url_input = TextInput(
            text=self.storage.get_server_url() or 'https://your-server.com/api',
            multiline=False,
            size_hint=(0.7, 1)
        )
        url_layout.add_widget(self.url_input)
        self.layout.add_widget(url_layout)
        
        # Status label
        self.status_label = Label(
            text='Status: Stopped',
            size_hint=(1, 0.1),
            color=(1, 0, 0, 1)
        )
        self.layout.add_widget(self.status_label)
        
        # Log area
        self.log_label = Label(
            text='Logs will appear here...',
            size_hint=(1, 0.5),
            text_size=(None, None),
            valign='top',
            halign='left'
        )
        self.layout.add_widget(self.log_label)
        
        # Control buttons
        button_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        self.start_button = Button(
            text='Start Service',
            on_press=self.start_service
        )
        button_layout.add_widget(self.start_button)
        
        self.stop_button = Button(
            text='Stop Service',
            on_press=self.stop_service,
            disabled=True
        )
        button_layout.add_widget(self.stop_button)
        
        self.layout.add_widget(button_layout)
        
        # Request permissions on Android
        if platform == 'android':
            self.request_android_permissions()
        
        return self.layout
    
    def request_android_permissions(self):
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION,
            Permission.READ_SMS,
            Permission.RECEIVE_SMS,
            Permission.READ_PHONE_STATE,
            Permission.BATTERY_STATS,
            Permission.INTERNET,
            Permission.ACCESS_NETWORK_STATE,
        ])
        self.log('Permissions requested')
    
    def start_service(self, instance):
        if self.running:
            return
        
        # Save server URL
        server_url = self.url_input.text.strip()
        if not server_url:
            self.log('Error: Please enter server URL')
            return
        
        self.storage.save_server_url(server_url)
        self.config.set_server_url(server_url)
        
        # Initialize services
        self.location_service = LocationService(self.config, self.log)
        self.device_service = DeviceService(self.config, self.log)
        self.message_service = MessageService(self.config, self.log)
        self.notification_service = NotificationService(self.config, self.log)
        
        # Start services in background
        threading.Thread(target=self._run_services, daemon=True).start()
        
        self.running = True
        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.url_input.disabled = True
        self.status_label.text = 'Status: Running'
        self.status_label.color = (0, 1, 0, 1)
        self.log('Services started successfully')
    
    def _run_services(self):
        # Start location tracking
        self.location_service.start()
        
        # Send device info immediately and periodically
        self.device_service.send_device_info()
        Clock.schedule_interval(
            lambda dt: self.device_service.send_device_info(),
            300  # Every 5 minutes
        )
        
        # Start message monitoring
        if platform == 'android':
            self.message_service.start()
        
        # Start notification monitoring
        if platform == 'android':
            self.notification_service.start()
    
    def stop_service(self, instance):
        if not self.running:
            return
        
        # Stop all services
        if self.location_service:
            self.location_service.stop()
        if self.message_service:
            self.message_service.stop()
        if self.notification_service:
            self.notification_service.stop()
        
        self.running = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.url_input.disabled = False
        self.status_label.text = 'Status: Stopped'
        self.status_label.color = (1, 0, 0, 1)
        self.log('Services stopped')
    
    def log(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_text = f'[{timestamp}] {message}\n'
        
        # Update log on main thread
        Clock.schedule_once(lambda dt: self._update_log(log_text), 0)
    
    def _update_log(self, log_text):
        current_text = self.log_label.text
        if current_text == 'Logs will appear here...':
            current_text = ''
        
        # Keep last 20 lines
        lines = (current_text + log_text).split('\n')
        self.log_label.text = '\n'.join(lines[-20:])
    
    def on_pause(self):
        # Keep running in background
        return True
    
    def on_resume(self):
        pass

if __name__ == '__main__':
    PhoneTrackerApp().run()