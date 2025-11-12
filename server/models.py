# server/models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class LocationModel:
    device_id: str
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    bearing: Optional[float] = None

@dataclass
class DeviceModel:
    device_id: str
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    android_version: Optional[str] = None
    sdk_version: Optional[int] = None
    battery_level: Optional[int] = None
    battery_status: Optional[str] = None
    storage_total: Optional[int] = None
    storage_available: Optional[int] = None
    ram_total: Optional[int] = None
    ram_available: Optional[int] = None
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    imei: Optional[str] = None
    sim_serial: Optional[str] = None
    phone_number: Optional[str] = None

@dataclass
class MessageModel:
    device_id: str
    sender: Optional[str] = None
    recipient: Optional[str] = None
    message_body: Optional[str] = None
    message_type: Optional[str] = None
    timestamp: Optional[int] = None
    read_status: Optional[bool] = None

@dataclass
class NotificationModel:
    device_id: str
    app_name: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None
    package_name: Optional[str] = None
    timestamp: Optional[int] = None