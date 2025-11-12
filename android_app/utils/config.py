# android_app/utils/config.py
import uuid
from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass
    Settings = autoclass('android.provider.Settings')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')

class Config:
    def __init__(self):
        self.server_url = ''
        self.device_id = self._get_or_create_device_id()
        
    def _get_or_create_device_id(self):
        """Get unique device ID"""
        if platform == 'android':
            try:
                activity = PythonActivity.mActivity
                context = activity.getApplicationContext()
                content_resolver = context.getContentResolver()
                
                # Get Android ID
                android_id = Settings.Secure.getString(
                    content_resolver,
                    Settings.Secure.ANDROID_ID
                )
                
                if android_id and android_id != '9774d56d682e549c':
                    return android_id
            except Exception as e:
                print(f'Error getting Android ID: {e}')
        
        # Fallback to UUID
        return str(uuid.uuid4())
    
    def get_device_id(self):
        return self.device_id
    
    def set_server_url(self, url):
        self.server_url = url.rstrip('/')
    
    def get_server_url(self):
        return self.server_url