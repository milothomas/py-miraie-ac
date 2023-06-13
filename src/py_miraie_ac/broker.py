"""The MQTT broker implemetation"""

import json
import math
import random
import ssl
from typing import Callable
from paho.mqtt import client as paho
from py_miraie_ac.enums import FanMode, HVACMode, PowerMode, PresetMode, SwingMode

class MirAIeBroker:
    """The MirAIe Broker class"""

    __host: str = "mqtt.miraie.in"
    __port: int = 8883
    __useSsl: bool = True
    __username: str
    __password: str
    __topics: list[str] = []
    __callbacks: dict[str, list[Callable]] = {}
    __client: paho.Client
    __get_access_token_callback: Callable

    def init_broker(self, username: str, password: str, get_access_token_callback: Callable):
        """Initializes the MQTT client"""
        self.__username = username
        self.__password = password
        self.__get_access_token_callback = get_access_token_callback
        self.__init_mqtt_client()

    def set_topics(self, topics: list[str]):
        """Sets the topics to subscribe to"""
        self.__topics = topics

    def register_callback(self, topic: str, callback: Callable):
        """Registers callbacks for a given topic"""
        self.__callbacks[topic] = callback

    def remove_callback(self, topic: str):
        """Removes an existing callback"""
        self.__callbacks.pop(topic, None)

    def connect(self):
        """Connects to MirAIe"""
        self.__client.connect(host=self.__host, port=self.__port)
        self.__client.loop_start()

    def reconnect(self, password: str):
        """Reconnects to MirAIe"""
        self.__password = password
        self.__client.username_pw_set(
            username=self.__username, password=self.__password
        )
        self.connect()

    def disconnect(self):
        """Disconnects from MirAIe"""
        self.__client.loop_stop()
        self.__client.disconnect()

    def set_temperature(self, topic: str, value: float):
        """Sets the Temperature to the given value"""
        message = self.__build_temp_message(value)
        self.__client.publish(topic, message)

    def set_power(self, topic: str, value: PowerMode):
        """Sets the Power to the given value"""
        message = self.__build_power_message(value)
        self.__client.publish(topic, message)

    def set_hvac_mode(self, topic: str, value: HVACMode):
        """Sets the Mode to the given value"""
        message = self.__build_hvac_mode_message(value)
        self.__client.publish(topic, message)

    def set_fan_mode(self, topic: str, value: FanMode):
        """Sets the Fan to the given value"""
        message = self.__build_fan_mode_message(value)
        self.__client.publish(topic, message)

    def set_preset_mode(self, topic: str, value: PresetMode):
        """Sets the Preset to the given value"""
        message = self.__build_preset_mode_message(value)
        self.__client.publish(topic, message)

    def set_vertical_swing_mode(self, topic: str, value: SwingMode):
        """Sets the Vertical Swing to the given value"""
        message = self.__build_vertical_swing_mode_message(value)
        self.__client.publish(topic, message)

    def set_horizontal_swing_mode(self, topic: str, value: SwingMode):
        """Sets the Horizontal Swing to the given value"""
        message = self.__build_horizontal_swing_mode_message(value)
        self.__client.publish(topic, message)

    def __generate_client_id(self):
        return (
            f"an{self.__generate_random_number(16)}{self.__generate_random_number(5)}"
        )

    def __generate_random_number(self, length: int):
        value = math.floor(random.random() * math.pow(10, length))
        return str(value)

    def __init_mqtt_client(self):
        self.__client = paho.Client(
            client_id=self.__generate_client_id(),
            transport="tcp",
            protocol=paho.MQTTv31,
            clean_session=False,
        )
        self.__client.username_pw_set(
            username=self.__username, password=self.__password
        )
        self.__client.on_connect = self.__on_mqtt_connected
        self.__client.on_disconnect = self.__on_mqtt_disconnected
        self.__client.on_message = self.__on_mqtt_message_received

        if self.__useSsl:
            self.__client.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED)

    def __on_mqtt_connected(self, client: paho.Client, user_data, flags, rc):
        for topic in self.__topics:
            client.subscribe(topic, qos=1)

    def __on_mqtt_disconnected(self, client: paho.Client, user_data, rc):
        def callback(username: str, password: str):
            self.__client.username_pw_set(username, password)
            self.__client.reconnect()

        if rc != 0:
            self.__get_access_token_callback(callback)

    def __on_mqtt_message_received(self, client: paho.Client, user_data, message):
        parsed = json.loads(message.payload.decode("utf-8"))
        callback_func = self.__callbacks.get(message.topic)
        callback_func(parsed)

    def __build_power_message(self, mode: PowerMode):
        message = self.__build_base_message()
        message["ps"] = str(mode.value)
        return json.dumps(message)

    def __build_temp_message(self, temp: float):
        message = self.__build_base_message()
        message["actmp"] = str(temp)
        return json.dumps(message)

    def __build_hvac_mode_message(self, mode: HVACMode):
        message = self.__build_base_message()
        message["acmd"] = str(mode.value)
        return json.dumps(message)

    def __build_fan_mode_message(self, mode: FanMode):
        message = self.__build_base_message()
        message["acfs"] = str(mode.value)
        return json.dumps(message)

    def __build_preset_mode_message(self, mode: PresetMode):
        message = self.__build_base_message()

        if mode == PresetMode.NONE:
            message["acem"] = "off"
            message["acpm"] = "off"
        elif mode == PresetMode.ECO:
            message["acem"] = "on"
            message["acpm"] = "off"
            message["actmp"] = 26.0
        elif mode == PresetMode.BOOST:
            message["acem"] = "off"
            message["acpm"] = "on"
        return json.dumps(message)

    def __build_vertical_swing_mode_message(self, mode: SwingMode):
        message = self.__build_base_message()
        message["acvs"] = mode.value
        return json.dumps(message)

    def __build_horizontal_swing_mode_message(self, mode: SwingMode):
        message = self.__build_base_message()
        message["achs"] = mode.value
        return json.dumps(message)

    def __build_base_message(self):
        return {
            "ki": 1,
            "cnt": "an",
            "sid": "1",
        }
