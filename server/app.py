# server/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
from database import Database
from models import LocationModel, DeviceModel, MessageModel, NotificationModel

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'phone_tracker')
}

db = Database(db_config)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/location', methods=['POST'])
def save_location():
    try:
        data = request.json
        location = LocationModel(
            device_id=data.get('device_id'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            altitude=data.get('altitude'),
            accuracy=data.get('accuracy'),
            speed=data.get('speed'),
            bearing=data.get('bearing')
        )
        
        result = db.insert_location(location)
        return jsonify({'success': True, 'id': result}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/device', methods=['POST'])
def save_device():
    try:
        data = request.json
        device = DeviceModel(
            device_id=data.get('device_id'),
            model=data.get('model'),
            manufacturer=data.get('manufacturer'),
            android_version=data.get('android_version'),
            sdk_version=data.get('sdk_version'),
            battery_level=data.get('battery_level'),
            battery_status=data.get('battery_status'),
            storage_total=data.get('storage_total'),
            storage_available=data.get('storage_available'),
            ram_total=data.get('ram_total'),
            ram_available=data.get('ram_available'),
            screen_width=data.get('screen_width'),
            screen_height=data.get('screen_height'),
            imei=data.get('imei'),
            sim_serial=data.get('sim_serial'),
            phone_number=data.get('phone_number')
        )
        
        result = db.insert_device(device)
        return jsonify({'success': True, 'id': result}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/message', methods=['POST'])
def save_message():
    try:
        data = request.json
        message = MessageModel(
            device_id=data.get('device_id'),
            sender=data.get('sender'),
            recipient=data.get('recipient'),
            message_body=data.get('message_body'),
            message_type=data.get('message_type'),
            timestamp=data.get('timestamp'),
            read_status=data.get('read_status')
        )
        
        result = db.insert_message(message)
        return jsonify({'success': True, 'id': result}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notification', methods=['POST'])
def save_notification():
    try:
        data = request.json
        notification = NotificationModel(
            device_id=data.get('device_id'),
            app_name=data.get('app_name'),
            title=data.get('title'),
            text=data.get('text'),
            package_name=data.get('package_name'),
            timestamp=data.get('timestamp')
        )
        
        result = db.insert_notification(notification)
        return jsonify({'success': True, 'id': result}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/<device_id>', methods=['GET'])
def get_locations(device_id):
    try:
        limit = request.args.get('limit', 100, type=int)
        locations = db.get_locations(device_id, limit)
        return jsonify({'success': True, 'data': locations}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/device/<device_id>', methods=['GET'])
def get_device(device_id):
    try:
        device = db.get_device_info(device_id)
        return jsonify({'success': True, 'data': device}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    db.initialize_database()
    app.run(host='0.0.0.0', port=8000, debug=False)