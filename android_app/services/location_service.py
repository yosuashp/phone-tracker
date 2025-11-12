# android_app/services/location_service.py
from kivy.utils import platform
from kivy.clock import Clock
import requests
import json

if platform == 'android':
    from plyer import gps

class LocationService:
    def __init__(self, config, log_callback):
        self.config = config
        self.log = log_callback
        self.running = False
        self.last_location = None
        
    def start(self):
        if platform != 'android':
            self.log('Location tracking only works on Android')
            return
        
        self.running = True
        try:
            gps.configure(on_location=self.on_location)
            gps.start(minTime=500, minDistance=10)  # Update every 5s or 10m
            self.log('Location tracking started')
        except Exception as e:
            self.log(f'Error starting location: {str(e)}')
    
    def stop(self):
        if platform == 'android':
            try:
                gps.stop()
                self.running = False
                self.log('Location tracking stopped')
            except Exception as e:
                self.log(f'Error stopping location: {str(e)}')
    
    def on_location(self, **kwargs):
        if not self.running:
            return
        
        try:
            location_data = {
                'device_id': self.config.get_device_id(),
                'latitude': kwargs.get('lat'),
                'longitude': kwargs.get('lon'),
                'altitude': kwargs.get('altitude'),
                'accuracy': kwargs.get('accuracy'),
                'speed': kwargs.get('speed'),
                'bearing': kwargs.get('bearing')
            }
            
            self.last_location = location_data
            self.send_location(location_data)
            
        except Exception as e:
            self.log(f'Location error: {str(e)}')
    
    def send_location(self, location_data):
        try:
            url = f"{self.config.get_server_url()}/location"
            response = requests.post(
                url,
                json=location_data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                self.log(f'Location sent: {location_data["latitude"]:.4f}, {location_data["longitude"]:.4f}')
            else:
                self.log(f'Location send failed: {response.status_code}')
                
        except requests.exceptions.RequestException as e:
            self.log(f'Network error sending location: {str(e)}')
        except Exception as e:
            self.log(f'Error sending location: {str(e)}')