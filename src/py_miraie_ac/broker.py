"""The MQTT broker implemetation"""

import json
import math
import random
import ssl
from typing import Callable
from paho.mqtt import client as paho
from .enums import FanMode, HVACMode, PowerMode, PresetMode, SwingMode

class MirAIeBroker:
    """The MirAIe Broker class"""

    _host: str = "mqtt.miraie.in"
    _port: int = 8883
    _useSsl: bool = True
    _username: str
    _password: str
    _topics: list[str] = []
    _callbacks: dict[str, list[Callable]] = {}
    _client: paho.Client
    _get_access_token_callback: Callable

    def __init__(self):
        self._client = paho.Client(
            client_id=self._generate_client_id(),
            transport="tcp",
            protocol=paho.MQTTv31,
            clean_session=False,
        )

    def init_broker(self, username: str, password: str, get_access_token_callback: Callable):
        """Initializes the MQTT client"""
        self._username = username
        self._password = password
        self._get_access_token_callback = get_access_token_callback
        self._init_mqtt_client()

    def set_topics(self, topics: list[str]):
        """Sets the topics to subscribe to"""
        self._topics = topics

    def register_callback(self, topic: str, callback: Callable):
        """Registers callbacks for a given topic"""
        self._callbacks[topic] = callback

    def remove_callback(self, topic: str):
        """Removes an existing callback"""
        self._callbacks.pop(topic, None)

    def connect(self):
        """Connects to MirAIe"""
        self._client.connect(host=self._host, port=self._port)
        self._client.loop_start()

    def reconnect(self, password: str):
        """Reconnects to MirAIe"""
        self._password = password
        self._client.username_pw_set(
            username=self._username, password=self._password
        )
        self.connect()

    def disconnect(self):
        """Disconnects from MirAIe"""
        self._client.loop_stop()
        if self._client.is_connected():
            self._client.disconnect()

    def set_temperature(self, topic: str, value: float):
        """Sets the Temperature to the given value"""
        message = self._build_temp_message(value)
        self._client.publish(topic, message)

    def set_power(self, topic: str, value: PowerMode):
        """Sets the Power to the given value"""
        message = self._build_power_message(value)
        self._client.publish(topic, message)

    def set_hvac_mode(self, topic: str, value: HVACMode):
        """Sets the Mode to the given value"""
        message = self._build_hvac_mode_message(value)
        self._client.publish(topic, message)

    def set_fan_mode(self, topic: str, value: FanMode):
        """Sets the Fan to the given value"""
        message = self._build_fan_mode_message(value)
        self._client.publish(topic, message)

    def set_preset_mode(self, topic: str, value: PresetMode):
        """Sets the Preset to the given value"""
        message = self._build_preset_mode_message(value)
        self._client.publish(topic, message)

    def set_vertical_swing_mode(self, topic: str, value: SwingMode):
        """Sets the Vertical Swing to the given value"""
        message = self._build_vertical_swing_mode_message(value)
        self._client.publish(topic, message)

    def set_horizontal_swing_mode(self, topic: str, value: SwingMode):
        """Sets the Horizontal Swing to the given value"""
        message = self._build_horizontal_swing_mode_message(value)
        self._client.publish(topic, message)

    def _generate_client_id(self):
        return (
            f"an{self._generate_random_number(16)}{self._generate_random_number(5)}"
        )

    def _generate_random_number(self, length: int):
        value = math.floor(random.random() * math.pow(10, length))
        return str(value)

    def _init_mqtt_client(self):
        self._client.username_pw_set(
            username=self._username, password=self._password
        )
        self._client.on_connect = self._on_mqtt_connected
        self._client.on_disconnect = self._on_mqtt_disconnected
        self._client.on_message = self._on_mqtt_message_received

        if self._useSsl:
            self._client.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED)

    def _on_mqtt_connected(self, client: paho.Client, user_data, flags, rc):
        for topic in self._topics:
            client.subscribe(topic, qos=1)

    def _on_mqtt_disconnected(self, client: paho.Client, user_data, rc):
        def callback(username: str, password: str):
            self._client.username_pw_set(username, password)
            self._client.reconnect()

        if rc != 0:
            self._get_access_token_callback(callback)

    def _on_mqtt_message_received(self, client: paho.Client, user_data, message):
        parsed = json.loads(message.payload.decode("utf-8"))
        callback_func = self._callbacks.get(message.topic)
        callback_func(parsed)

    def _build_power_message(self, mode: PowerMode):
        message = self._build_base_message()
        message["ps"] = str(mode.value)
        return json.dumps(message)

    def _build_temp_message(self, temp: float):
        message = self._build_base_message()
        message["actmp"] = str(temp)
        return json.dumps(message)

    def _build_hvac_mode_message(self, mode: HVACMode):
        message = self._build_base_message()
        message["acmd"] = str(mode.value)
        return json.dumps(message)

    def _build_fan_mode_message(self, mode: FanMode):
        message = self._build_base_message()
        message["acfs"] = str(mode.value)
        return json.dumps(message)

    def _build_preset_mode_message(self, mode: PresetMode):
        message = self._build_base_message()

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

    def _build_vertical_swing_mode_message(self, mode: SwingMode):
        message = self._build_base_message()
        message["acvs"] = mode.value
        return json.dumps(message)

    def _build_horizontal_swing_mode_message(self, mode: SwingMode):
        message = self._build_base_message()
        message["achs"] = mode.value
        return json.dumps(message)

    def _build_base_message(self):
        return {
            "ki": 1,
            "cnt": "an",
            "sid": "1",
        }
