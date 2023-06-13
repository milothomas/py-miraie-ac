"""The MirAIe API module"""

import math
import random
import asyncio
import aiohttp
from py_miraie_ac.broker import MirAIeBroker
from py_miraie_ac.device import Device
from py_miraie_ac.constants import DEVICE_DETAILS_URL, HOMES_URL,HTTP_CLIENT_ID,LOGIN_URL,STATUS_URL
from py_miraie_ac.deviceStatus import DeviceStatus
from py_miraie_ac.enums import (
    AuthType,
    DisplayState,
    FanMode,
    HVACMode,
    PowerMode,
    PresetMode,
    SwingMode,
)
from py_miraie_ac.exceptions import AuthException
from py_miraie_ac.home import Home
from py_miraie_ac.user import User
from py_miraie_ac.utils import to_float

class MirAIeAPI:
    """The MirAIe API class"""
    __auth_type: str
    __login_id: str
    __password: str
    __http_session: aiohttp.ClientSession
    __user: User
    __home: Home
    __topics: list[str] = []
    __broker: MirAIeBroker

    @property
    def devices(self) -> list[Device]:
        """Returns a list of available devices."""
        return list(self.__home.devices.values())

    def __init__(self, auth_type: AuthType, login_id: str, password: str):
        self.__auth_type = str(auth_type.value)
        self.__login_id = login_id
        self.__password = password
        self.__http_session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self.__http_session.close()
        self.__broker.disconnect()

    async def initialize(self):
        """Initializes the MirAIe API"""

        self.__user = await self.__login()
        self.__broker = MirAIeBroker()

        self.__home = await self.__get_home_details()
        self.__broker.set_topics(self.__topics)
        self.__broker.init_broker(self.__home.home_id, self.__user.access_token, self.reconnect_broker)
        self.__broker.connect()

    def reconnect_broker(self, reconnect_callback: callable):
        """Authenticates with MirAIe and reconnects to MQTT server with the new credentials"""
        loop = self.__http_session.loop
        fut = asyncio.run_coroutine_threadsafe(self.__login(), loop)

        self.__user = fut.result()
        reconnect_callback(self.__home.home_id, self.__user.access_token)

    async def __login(self):
        data = {
            "clientId": HTTP_CLIENT_ID,
            "password": self.__password,
            "scope": self.__get_scope(),
        }

        data[self.__auth_type] = self.__login_id
        response = await self.__http_session.post(LOGIN_URL, json=data)

        if response.status == 200:
            json = await response.json()
            return User(
                access_token=json["accessToken"],
                refresh_token=json["refreshToken"],
                user_id=json["userId"],
                expires_in=json["expiresIn"],
            )

        raise AuthException("Authentication failed")

    async def __get_home_details(self):
        response = await self.__http_session.get(
            HOMES_URL, headers=self.__build_http_headers()
        )
        resp = await response.json()
        return await self.__parse_home_details(resp[0])

    async def __parse_home_details(self, json_response):
        devices: list[Device] = []

        for space in json_response["spaces"]:
            space_name = space["spaceName"]
            for device in space["devices"]:
                device_id = device["deviceId"]
                topic = str(device["topic"][0])
                device_details = await self.__get_device_details(device_id)
                device_status = await self.__get_device_status(device_id)

                device = Device(
                    device_id=device_id,
                    name=str(device["deviceName"]).lower().replace(" ", "-"),
                    friendly_name=device["deviceName"],
                    control_topic=f"{topic}/control",
                    status_topic=f"{topic}/status",
                    connection_status_topic=f"{topic}/connectionStatus",
                    model_name=device_details["modelName"],
                    mac_address=device_details["macAddress"],
                    category=device_details["category"],
                    brand=device_details["brand"],
                    firmware_version=device_details["firmwareVersion"],
                    serial_number=device_details["serialNumber"],
                    model_number=device_details["modelNumber"],
                    product_serial_number=device_details["productSerialNumber"],
                    status=device_status,
                    broker=self.__broker,
                    area_name=space_name,
                )

                self.__topics.append(device.status_topic)
                self.__topics.append(device.connection_status_topic)
                devices.append(device)

        return Home(home_id=json_response["homeId"], devices=devices)

    async def __get_device_details(self, device_id: str):
        url = f"{DEVICE_DETAILS_URL}/{device_id}"

        response = await self.__http_session.get(
            url,
            headers=self.__build_http_headers(),
        )

        json = await response.json()
        return json[0]

    async def __get_device_status(self, device_id: str):
        status: DeviceStatus

        response = await self.__http_session.get(
            STATUS_URL.replace("{deviceId}", device_id),
            headers=self.__build_http_headers(),
        )

        json = await response.json()
        status = DeviceStatus(
            is_online=json["onlineStatus"] == "true",
            temperature=to_float(json["actmp"]),
            room_temp=to_float(json["rmtmp"]),
            power_mode=PowerMode(json["ps"]),
            fan_mode=FanMode(json["acfs"]),
            display_state=DisplayState(json["acdc"]),
            hvac_mode=HVACMode(json["acmd"]),
            preset_mode=PresetMode.BOOST
            if json["acpm"] == "on"
            else PresetMode.ECO
            if json["acem"] == "on"
            else PresetMode.NONE,
            vertical_swing_mode=SwingMode(json["acvs"]),
            horizontal_swing_mode=SwingMode(json["achs"]),
        )

        return status

    def __build_http_headers(self):
        return {
            "Authorization": f"Bearer {self.__user.access_token}"
            ,"Content-Type": "application/json",
        }

    def __get_scope(self):
        rnd = math.floor(random.random() * 1000000000)
        return f"an{str(rnd)}"
