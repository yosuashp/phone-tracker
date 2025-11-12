# server/database.py
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

class Database:
    def __init__(self, config):
        self.config = config
    
    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = mysql.connector.connect(**self.config)
            yield conn
        except Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def initialize_database(self):
        """Create tables if not exists"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Locations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS locations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id VARCHAR(255) NOT NULL,
                    latitude DOUBLE NOT NULL,
                    longitude DOUBLE NOT NULL,
                    altitude DOUBLE,
                    accuracy FLOAT,
                    speed FLOAT,
                    bearing FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_device_id (device_id),
                    INDEX idx_created_at (created_at)
                )
            """)
            
            # Devices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id VARCHAR(255) UNIQUE NOT NULL,
                    model VARCHAR(255),
                    manufacturer VARCHAR(255),
                    android_version VARCHAR(50),
                    sdk_version INT,
                    battery_level INT,
                    battery_status VARCHAR(50),
                    storage_total BIGINT,
                    storage_available BIGINT,
                    ram_total BIGINT,
                    ram_available BIGINT,
                    screen_width INT,
                    screen_height INT,
                    imei VARCHAR(255),
                    sim_serial VARCHAR(255),
                    phone_number VARCHAR(50),
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id VARCHAR(255) NOT NULL,
                    sender VARCHAR(255),
                    recipient VARCHAR(255),
                    message_body TEXT,
                    message_type VARCHAR(20),
                    timestamp BIGINT,
                    read_status BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_device_id (device_id),
                    INDEX idx_timestamp (timestamp)
                )
            """)
            
            # Notifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    device_id VARCHAR(255) NOT NULL,
                    app_name VARCHAR(255),
                    title VARCHAR(500),
                    text TEXT,
                    package_name VARCHAR(255),
                    timestamp BIGINT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_device_id (device_id),
                    INDEX idx_timestamp (timestamp)
                )
            """)
            
            conn.commit()
            print("Database tables initialized successfully")
    
    def insert_location(self, location):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO locations 
                (device_id, latitude, longitude, altitude, accuracy, speed, bearing)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                location.device_id,
                location.latitude,
                location.longitude,
                location.altitude,
                location.accuracy,
                location.speed,
                location.bearing
            )
            cursor.execute(query, values)
            conn.commit()
            return cursor.lastrowid
    
    def insert_device(self, device):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO devices 
                (device_id, model, manufacturer, android_version, sdk_version, 
                 battery_level, battery_status, storage_total, storage_available,
                 ram_total, ram_available, screen_width, screen_height,
                 imei, sim_serial, phone_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    model=VALUES(model),
                    manufacturer=VALUES(manufacturer),
                    android_version=VALUES(android_version),
                    sdk_version=VALUES(sdk_version),
                    battery_level=VALUES(battery_level),
                    battery_status=VALUES(battery_status),
                    storage_total=VALUES(storage_total),
                    storage_available=VALUES(storage_available),
                    ram_total=VALUES(ram_total),
                    ram_available=VALUES(ram_available),
                    screen_width=VALUES(screen_width),
                    screen_height=VALUES(screen_height),
                    imei=VALUES(imei),
                    sim_serial=VALUES(sim_serial),
                    phone_number=VALUES(phone_number)
            """
            values = (
                device.device_id, device.model, device.manufacturer,
                device.android_version, device.sdk_version, device.battery_level,
                device.battery_status, device.storage_total, device.storage_available,
                device.ram_total, device.ram_available, device.screen_width,
                device.screen_height, device.imei, device.sim_serial, device.phone_number
            )
            cursor.execute(query, values)
            conn.commit()
            return cursor.lastrowid
    
    def insert_message(self, message):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO messages 
                (device_id, sender, recipient, message_body, message_type, timestamp, read_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                message.device_id, message.sender, message.recipient,
                message.message_body, message.message_type, message.timestamp,
                message.read_status
            )
            cursor.execute(query, values)
            conn.commit()
            return cursor.lastrowid
    
    def insert_notification(self, notification):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO notifications 
                (device_id, app_name, title, text, package_name, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                notification.device_id, notification.app_name, notification.title,
                notification.text, notification.package_name, notification.timestamp
            )
            cursor.execute(query, values)
            conn.commit()
            return cursor.lastrowid
    
    def get_locations(self, device_id, limit=100):
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT * FROM locations 
                WHERE device_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """
            cursor.execute(query, (device_id, limit))
            return cursor.fetchall()
    
    def get_device_info(self, device_id):
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM devices WHERE device_id = %s"
            cursor.execute(query, (device_id,))
            return cursor.fetchone()