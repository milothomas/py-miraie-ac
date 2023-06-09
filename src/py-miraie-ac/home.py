"""Represents a home"""
from device import Device

class Home:
    """The Home class"""
    home_id: str
    devices: dict[str, Device]

    def __init__(self, home_id: str, devices: list[Device]):
        self.home_id = home_id
        self.devices = dict((d.device_id, d) for d in devices)

    def get_device(self, device_id: str):
        """Gets a device by its ID"""
        if device_id in self.devices:
            return self.devices[device_id]
