import math
import random
import aiohttp
from broker import MirAIeBroker
import constants
from device import Device
from deviceStatus import DeviceStatus
from enums import (
    AuthType,
    DisplayState,
    FanMode,
    HVACMode,
    PowerMode,
    PresetMode,
    SwingMode,
)
from home import Home
from user import User


class MirAIeAPI:
    __authType: str
    __loginId: str
    __password: str
    __httpSession: aiohttp.ClientSession
    __user: User
    __home: Home
    __topics: list[str] = []
    __broker: MirAIeBroker

    def __init__(self, authType: AuthType, loginId: str, password: str):
        self.__authType = str(authType.value)
        self.__loginId = loginId
        self.__password = password
        self.__httpSession = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self.__httpSession.close()

    async def init(self):
        self.__user = await self.__login()
        self.__broker = MirAIeBroker(
            self.__user.userId, self.__user.accessToken, self.getNewToken
        )

        self.__home = await self.__getHomeDetails()

        self.__broker.setTopics(self.__topics)
        self.__broker.connect()

        self.__showHomeDetails()

    async def getNewToken(self):
        self.__user = await self.__login()
        # callback(self.__user.accessToken)
        self.__broker.reconnect(self.__user.accessToken)

    def getDevices(self):
        if self.__home is not None:
            return self.__home.devices.values()
        return list[Device]

    def __showHomeDetails(self):
        print("id:", self.__home.id)
        for device_id, device in self.__home.devices.items():
            print("Name:", device.friendlyName)

    #################################################################################################################
    #                                                                                                               #
    #################################################################################################################

    async def __login(self):
        data = {
            "clientId": constants.httpClientId,
            "password": self.__password,
            "scope": self.__getScope(),
        }

        data[self.__authType] = self.__loginId
        response = await self.__httpSession.post(constants.loginUrl, json=data)

        if response.status == 200:
            json = await response.json()
            return User(
                accessToken=json["accessToken"],
                refreshToken=json["refreshToken"],
                userId=json["userId"],
                expiresIn=json["expiresIn"],
            )

        raise Exception("Authentication failed")

    async def __getHomeDetails(self):
        response = await self.__httpSession.get(
            constants.homesUrl, headers=self.__buildHttpHeaders()
        )
        resp = await response.json()
        return await self.__parseHomeDetails(resp[0])

    async def __parseHomeDetails(self, jsonResponse):
        devices: list[Device] = []

        for space in jsonResponse["spaces"]:
            for device in space["devices"]:
                deviceId = device["deviceId"]
                topic = str(device["topic"][0])
                deviceDetails = await self.getDeviceDetails(deviceId)
                deviceStatus = await self.getDeviceStatus(deviceId)

                device = Device(
                    id=deviceId,
                    name=str(device["deviceName"]).lower().replace(" ", "-"),
                    friendlyName=device["deviceName"],
                    controlTopic=f"{topic}/control",
                    statusTopic=f"{topic}/status",
                    connectionStatusTopic=f"{topic}/connectionStatus",
                    modelName=deviceDetails["modelName"],
                    macAddress=deviceDetails["macAddress"],
                    category=deviceDetails["category"],
                    brand=deviceDetails["brand"],
                    firmwareVersion=deviceDetails["firmwareVersion"],
                    serialNumber=deviceDetails["serialNumber"],
                    modelNumber=deviceDetails["modelNumber"],
                    productSerialNumber=deviceDetails["productSerialNumber"],
                    status=deviceStatus,
                    broker=self.__broker,
                )
                self.__topics.append(device.statusTopic)
                self.__topics.append(device.connectionStatusTopic)
                devices.append(device)

        return Home(id=jsonResponse["homeId"], devices=devices)

    async def getDeviceDetails(self, deviceId: str):
        url = f"{constants.deviceDetailsUrl}/{deviceId}"

        response = await self.__httpSession.get(
            url,
            headers=self.__buildHttpHeaders(),
        )

        json = await response.json()
        return json[0]

    async def getDeviceStatus(self, deviceId: str):
        status: DeviceStatus

        response = await self.__httpSession.get(
            constants.statusUrl.replace("{deviceId}", deviceId),
            headers=self.__buildHttpHeaders(),
        )

        json = await response.json()
        status = DeviceStatus(
            isOnline=json["onlineStatus"] == "true",
            temperature=toFloat(json["actmp"]),
            roomTemp=toFloat(json["rmtmp"]),
            powerMode=PowerMode(json["ps"]),
            fanMode=FanMode(json["acfs"]),
            swingMode=SwingMode(json["acvs"]),
            displayState=DisplayState(json["acdc"]),
            hvacMode=HVACMode(json["acmd"]),
            presetMode=PresetMode.BOOST
            if json["acpm"] == "on"
            else PresetMode.ECO
            if json["acem"] == "on"
            else PresetMode.NONE,
        )

        return status

    def __buildHttpHeaders(self):
        return {
            "Authorization": f"Bearer {self.__user.accessToken}",
            "Content-Type": "application/json",
        }

    def __getScope(self):
        rnd = math.floor(random.random() * 1000000000)
        return f"an{str(rnd)}"


def toFloat(value: str) -> float:
    if value is None:
        return -1.0
    try:
        return float(value)
    except:
        return -1.0
