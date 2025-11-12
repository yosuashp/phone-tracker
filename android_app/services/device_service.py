# android_app/services/device_service.py
from kivy.utils import platform
import requests

if platform == 'android':
    from jnius import autoclass, cast
    
    Build = autoclass('android.os.Build')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    BatteryManager = autoclass('android.os.BatteryManager')
    ActivityManager = autoclass('android.app.ActivityManager')
    StatFs = autoclass('android.os.StatFs')
    Environment = autoclass('android.os.Environment')
    TelephonyManager = autoclass('android.telephony.TelephonyManager')

class DeviceService:
    def __init__(self, config, log_callback):
        self.config = config
        self.log = log_callback
        
    def get_device_info(self):
        if platform != 'android':
            return self._get_dummy_device_info()
        
        try:
            activity = PythonActivity.mActivity
            context = activity.getApplicationContext()
            
            # Basic device info
            model = Build.MODEL
            manufacturer = Build.MANUFACTURER
            android_version = Build.VERSION.RELEASE
            sdk_version = Build.VERSION.SDK_INT
            
            # Battery info
            battery_manager = cast(
                'android.os.BatteryManager',
                context.getSystemService(Context.BATTERY_SERVICE)
            )
            battery_level = battery_manager.getIntProperty(
                BatteryManager.BATTERY_PROPERTY_CAPACITY
            )
            
            # Storage info
            storage_path = Environment.getDataDirectory()
            stat = StatFs(storage_path.getPath())
            storage_total = stat.getTotalBytes()
            storage_available = stat.getAvailableBytes()
            
            # RAM info
            activity_manager = cast(
                'android.app.ActivityManager',
                context.getSystemService(Context.ACTIVITY_SERVICE)
            )
            mem_info = ActivityManager.MemoryInfo()
            activity_manager.getMemoryInfo(mem_info)
            ram_total = mem_info.totalMem
            ram_available = mem_info.availMem
            
            # Screen info
            display = activity.getWindowManager().getDefaultDisplay()
            point = autoclass('android.graphics.Point')()
            display.getSize(point)
            screen_width = point.x
            screen_height = point.y
            
            # Phone info
            telephony_manager = cast(
                'android.telephony.TelephonyManager',
                context.getSystemService(Context.TELEPHONY_SERVICE)
            )
            
            try:
                imei = telephony_manager.getDeviceId()
            except:
                imei = None
            
            try:
                sim_serial = telephony_manager.getSimSerialNumber()
            except:
                sim_serial = None
            
            try:
                phone_number = telephony_manager.getLine1Number()
            except:
                phone_number = None
            
            return {
                'device_id': self.config.get_device_id(),
                'model': model,
                'manufacturer': manufacturer,
                'android_version': android_version,
                'sdk_version': sdk_version,
                'battery_level': battery_level,
                'battery_status': 'charging',
                'storage_total': storage_total,
                'storage_available': storage_available,
                'ram_total': ram_total,
                'ram_available': ram_available,
                'screen_width': screen_width,
                'screen_height': screen_height,
                'imei': imei,
                'sim_serial': sim_serial,
                'phone_number': phone_number
            }
            
        except Exception as e:
            self.log(f'Error getting device info: {str(e)}')
            return None
    
    def _get_dummy_device_info(self):
        """For testing on non-Android platforms"""
        return {
            'device_id': self.config.get_device_id(),
            'model': 'Test Device',
            'manufacturer': 'Test',
            'android_version': '11',
            'sdk_version': 30,
            'battery_level': 85,
            'battery_status': 'not_charging',
            'storage_total': 64000000000,
            'storage_available': 32000000000,
            'ram_total': 4000000000,
            'ram_available': 2000000000,
            'screen_width': 1080,
            'screen_height': 2400,
            'imei': None,
            'sim_serial': None,
            'phone_number': None
        }
    
    def send_device_info(self):
        try:
            device_info = self.get_device_info()
            if not device_info:
                return
            
            url = f"{self.config.get_server_url()}/device"
            response = requests.post(
                url,
                json=device_info,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                self.log('Device info sent successfully')
            else:
                self.log(f'Device info send failed: {response.status_code}')
                
        except requests.exceptions.RequestException as e:
            self.log(f'Network error sending device info: {str(e)}')
        except Exception as e:
            self.log(f'Error sending device info: {str(e)}')