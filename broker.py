import asyncio
import json
import math
import random
import ssl
import certifi
from paho.mqtt import client as paho

from enums import FanMode, HVACMode, PowerMode, PresetMode, SwingMode


class MirAIeBroker:
    __host: str = "mqtt.miraie.in"
    __port: int = 8883
    __useSsl: bool = True
    __username: str
    __password: str
    __topics: list[str] = []
    __callbacks: dict[str, list[callable]] = {}


    def init_broker(self, username: str, password: str):
        self.__username = username
        self.__password = password
        self.__initMqttClient()

    def setTopics(self, topics: list[str]):
        self.__topics = topics

    def registerCallback(self, topic: str, callback):
        self.__callbacks[topic] = callback

    def removeCallback(self, topic: str):
        self.__callbacks.pop(topic, None)

    def connect(self):
        self.__client.connect(host=self.__host, port=self.__port)
        self.__client.loop_start()
    
    def reconnect(self, password: str):
        self.__password = password
        self.__client.username_pw_set(username=self.__username, password=self.__password)
        self.connect()

    
    def setTemperature(self, topic: str, value: float):
        message = self.__buildTempMessage(value)
        self.__client.publish(topic, message)

    def setPower(self, topic: str, value: PowerMode):
        message = self.__buildPowerMessage(value)
        self.__client.publish(topic, message)

    def setHVACMode(self, topic: str, value: HVACMode):
        message = self.__buildHVACModeMessage(value)
        self.__client.publish(topic, message)

    def setFanMode(self, topic: str, value: FanMode):
        message = self.__buildFanModeMessage(value)
        self.__client.publish(topic, message)

    def setPresetMode(self, topic: str, value: PresetMode):
        message = self.__buildPresetModeMessage(value)
        self.__client.publish(topic, message)

    def setSwingMode(self, topic: str, value: SwingMode):
        message = self.__buildSwingModeMessage(value)
        self.__client.publish(topic, message)

    def __generateClientId(self):
        return f"an{self.__generateRandomNumber(16)}{self.__generateRandomNumber(5)}"

    def __generateRandomNumber(self, len: int):
        value = math.floor(random.random() * math.pow(10, len))
        return str(value)

    def __initMqttClient(self):
        self.__client = paho.Client(client_id=self.__generateClientId(), transport="tcp", protocol=paho.MQTTv31, clean_session=False)
        self.__client.username_pw_set(
            username=self.__username, password=self.__password
        )
        self.__client.on_connect = self.__onMqttConnected
        self.__client.on_message = self.__onMqttMessageReceived
        self.__client.on_disconnect = self.__onMqttDisconnected
        self.__client.on_log = self.__onMqttLog


        # if self.__useSsl:
        #     context = ssl.create_default_context(cafile=certifi.where())
        #     self.__client.tls_set_context(context)
        #     self.__client.tls_insecure_set(True)

        self.__client.tls_set(certfile=None,
               keyfile=None,
               cert_reqs=ssl.CERT_REQUIRED)

    def __onMqttLog(self, client,userdata,level,buff):
        print("==========")
        print("MQTT LOG:", buff)
        print("level:", level)
        print("userData", userdata)
        print("==========")


    def __onMqttConnected(self, client: paho.Client, userData, flags, rc):
        for topic in self.__topics:
            client.subscribe(topic, qos=1)

    def __onMqttMessageReceived(self, client: paho.Client, userData, message):
        parsed = json.loads(message.payload.decode("utf-8"))

        callbackFunc = self.__callbacks.get(message.topic)
        callbackFunc(parsed)

    def __onMqttDisconnected(self, client: paho.Client, userData, rc):
        # def updateAccessToken(accessToken: str):
        #     self.__password = accessToken
        #     self.__client.username_pw_set(username=self.__username, password=self.__password)
        #     self.__client.reconnect()

        #if rc != 0:
            # loop = asyncio.new_event_loop()
            # loop.create_task(self.__getTokenFunc())
        print("mqtt disconnected")
            
    def __buildPowerMessage(self, mode: PowerMode):
        message = self.__buildBaseMessage()
        message["ps"] = str(mode.value)
        return json.dumps(message)
    
    def __buildTempMessage(self, temp: float):
        message = self.__buildBaseMessage()
        message["actmp"] = str(temp)
        return json.dumps(message)

    def __buildHVACModeMessage(self, mode: HVACMode):
        message = self.__buildBaseMessage()
        message["acmd"] = str(mode.value)
        return json.dumps(message)

    def __buildFanModeMessage(self, mode: FanMode):
        message = self.__buildBaseMessage()
        message["acfs"] = str(mode.value)
        return json.dumps(message)
    
    def __buildPresetModeMessage(self, mode: PresetMode):
        message = self.__buildBaseMessage()

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
    
    def __buildSwingModeMessage(self, mode: SwingMode):
        message = self.__buildBaseMessage()
        message["acvs"] = mode.value
        return json.dumps(message)
    
    def __buildBaseMessage(self):
        return {
            "ki": 1,
            "cnt": "an",
            "sid": "1",
        }