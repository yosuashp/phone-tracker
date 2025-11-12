# android_app/utils/storage.py
import json
import os
from kivy.app import App

class Storage:
    def __init__(self):
        self.settings_file = 'tracker_settings.json'
        self.settings = self._load_settings()
    
    def _get_data_dir(self):
        """Get app data directory"""
        try:
            app = App.get_running_app()
            if app:
                return app.user_data_dir
        except:
            pass
        return os.path.expanduser('~')
    
    def _get_settings_path(self):
        return os.path.join(self._get_data_dir(), self.settings_file)
    
    def _load_settings(self):
        try:
            settings_path = self._get_settings_path()
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f'Error loading settings: {e}')
        
        return {}
    
    def _save_settings(self):
        try:
            settings_path = self._get_settings_path()
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f)
        except Exception as e:
            print(f'Error saving settings: {e}')
    
    def save_server_url(self, url):
        self.settings['server_url'] = url
        self._save_settings()
    
    def get_server_url(self):
        return self.settings.get('server_url')