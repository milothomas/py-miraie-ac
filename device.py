from typing import Callable
from broker import MirAIeBroker
from deviceStatus import DeviceStatus
from enums import FanMode, HVACMode, PowerMode, PresetMode, SwingMode


class Device:
    __broker: MirAIeBroker

    def __init__(
        self,
        id: str,
        name: str,
        friendlyName: str,
        controlTopic: str,
        statusTopic: str,
        connectionStatusTopic: str,
        modelName: str,
        macAddress: str,
        category: str,
        brand: str,
        firmwareVersion: str,
        serialNumber: str,
        modelNumber: str,
        productSerialNumber: str,
        status: DeviceStatus,
        broker: MirAIeBroker
    ):
        self.id = id
        self.name = name
        self.friendlyName = friendlyName
        self.controlTopic = controlTopic
        self.statusTopic = statusTopic
        self.connectionStatusTopic = connectionStatusTopic
        self.modelName = modelName
        self.macAddress = macAddress
        self.category = category
        self.brand = brand
        self.firmwareVersion = firmwareVersion
        self.serialNumber = serialNumber
        self.modelNumber = modelNumber
        self.productSerialNumber = productSerialNumber
        self.status = status
        
        self.__broker = broker
        self.__callbacks = set()
        self.__broker.registerCallback(self.statusTopic, self.statusCallbackHandler)
        self.__broker.registerCallback(self.connectionStatusTopic, self.connectionCallbackHandler)

    def __publishState(self):
        for callback in self.__callbacks:
            callback()

    def statusCallbackHandler(self, status: DeviceStatus):
        self.status = status
        self.__publishState()

    def connectionCallbackHandler(self, isOnline: bool):
        self.status.isOnline = isOnline
        self.__publishState()

    def setTemperature(self, temp: float):
        self.__broker.setTemperature(self.controlTopic, temp)

    def turnOn(self):
        self.__broker.setPower(self.controlTopic, PowerMode.ON)

    def turnOff(self):
        self.__broker.setPower(self.controlTopic, PowerMode.OFF)

    def setHVACMode(self, mode: HVACMode):
        self.__broker.setHVACMode(self.controlTopic, mode)

    def setFanMode(self, mode: FanMode):
        self.__broker.setFanMode(self.controlTopic, mode)

    def setPresetMode(self, mode: PresetMode):
        self.__broker.setPresetMode(self.controlTopic, mode)

    def setSwingMode(self, mode: SwingMode):
        self.__broker.setSwingMode(self.controlTopic, mode)

    def registerCallback(self, callback: Callable[[], None]) -> None:
        self.__callbacks.add(callback)

    def removeCallback(self, callback: Callable[[], None]) -> None:
        self.__callbacks.discard(callback)