from device import Device


class Home:
    id: str
    devices: dict[str, Device]

    def __init__(self, id: str, devices: list[Device]):
        self.id = id
        self.devices = dict((d.id, d) for d in devices)

    def getDevice(self, deviceId: str):
        if deviceId in self.devices:
            return self.devices[deviceId]