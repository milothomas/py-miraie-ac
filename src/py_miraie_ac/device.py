"""The MirAIe device"""
from typing import Callable
from py_miraie_ac.broker import MirAIeBroker
from py_miraie_ac.deviceStatus import DeviceStatus
from py_miraie_ac.enums import DisplayState, FanMode, HVACMode, PowerMode, PresetMode, SwingMode
from py_miraie_ac.utils import to_float

class Device:
    """The MirAIe device class"""

    __broker: MirAIeBroker

    def __init__(
        self,
        device_id: str,
        name: str,
        friendly_name: str,
        control_topic: str,
        status_topic: str,
        connection_status_topic: str,
        model_name: str,
        mac_address: str,
        category: str,
        brand: str,
        firmware_version: str,
        serial_number: str,
        model_number: str,
        product_serial_number: str,
        status: DeviceStatus,
        broker: MirAIeBroker,
    ):
        self.device_id = device_id
        self.name = name
        self.friendly_name = friendly_name
        self.control_topic = control_topic
        self.status_topic = status_topic
        self.connection_status_topic = connection_status_topic
        self.model_name = model_name
        self.mac_address = mac_address
        self.category = category
        self.brand = brand
        self.firmware_version = firmware_version
        self.serial_number = serial_number
        self.model_number = model_number
        self.product_serial_number = product_serial_number
        self.status = status

        self.__broker = broker
        self.__callbacks = set()
        self.__broker.register_callback(self.status_topic, self.status_callback_handler)
        self.__broker.register_callback(
            self.connection_status_topic, self.connection_callback_handler
        )

    def __publish_state(self):
        for callback in self.__callbacks:
            callback()

    def status_callback_handler(self, status: dict):
        """Handles MQTT messages received on the status topic"""

        self.status = self.__parse_status_response(status)
        self.__publish_state()

    def __parse_status_response(self, json: dict) -> DeviceStatus:
        is_online = self.status.is_online
        if "onlineStatus" in json:
            is_online = json["onlineStatus"] == "true"

        device_status = DeviceStatus(
            is_online=is_online,
            temperature=to_float(json["actmp"]),
            room_temp=to_float(json["rmtmp"]),
            power_mode=PowerMode(json["ps"]),
            fan_mode=FanMode(json["acfs"]),
            swing_mode=SwingMode(json["acvs"]),
            display_state=DisplayState(json["acdc"]),
            hvac_mode=HVACMode(json["acmd"]),
            preset_mode=PresetMode.BOOST
            if json["acpm"] == "on"
            else PresetMode.ECO
            if json["acem"] == "on"
            else PresetMode.NONE,
        )

        return device_status

    def connection_callback_handler(self, status: dict):
        """Handles MQTT messages received on the connection status topic"""

        if "onlineStatus" in status:
            self.status.is_online = status["onlineStatus"] == "true"
            self.__publish_state()

    def set_temperature(self, temp: float):
        """Sets the temperature"""
        self.__broker.set_temperature(self.control_topic, temp)

    def turn_on(self):
        """Turns on the devie"""
        self.__broker.set_power(self.control_topic, PowerMode.ON)

    def turn_off(self):
        """Turns off the device"""
        self.__broker.set_power(self.control_topic, PowerMode.OFF)

    def set_hvac_mode(self, mode: HVACMode):
        """Sets the HVAC mode"""
        self.__broker.set_hvac_mode(self.control_topic, mode)

    def set_fan_mode(self, mode: FanMode):
        """Sets the fan mode"""
        self.__broker.set_fan_mode(self.control_topic, mode)

    def set_preset_mode(self, mode: PresetMode):
        """Sets the preset mode"""
        self.__broker.set_preset_mode(self.control_topic, mode)

    def set_swing_mode(self, mode: SwingMode):
        """Sets the swing mode"""
        self.__broker.set_swing_mode(self.control_topic, mode)

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Registers a callback function"""
        self.__callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Removes a callback function"""
        self.__callbacks.discard(callback)
