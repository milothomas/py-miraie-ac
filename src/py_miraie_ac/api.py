"""The MirAIe API module"""

import math
import random
import asyncio
from typing import Callable
import aiohttp
from .broker import MirAIeBroker
from .device import Device
from .constants import DEVICE_DETAILS_URL, HOMES_URL,HTTP_CLIENT_ID,LOGIN_URL,STATUS_URL
from .deviceStatus import DeviceStatus
from .enums import (
    AuthType,
    DisplayState,
    FanMode,
    HVACMode,
    PowerMode,
    PresetMode,
    SwingMode,
)
from .exceptions import AuthException, ConnectionException, MobileNotRegisteredException
from .home import Home
from .user import User
from .utils import to_float

class MirAIeAPI:
    """The MirAIe API class"""
    _auth_type: str
    _login_id: str
    _password: str
    _http_session: aiohttp.ClientSession
    _user: User
    _home: Home
    _topics: list[str] = []
    _broker: MirAIeBroker

    @property
    def devices(self) -> list[Device]:
        """Returns a list of available devices."""
        return list(self._home.devices.values())

    def __init__(self, auth_type: AuthType, login_id: str, password: str):
        self._auth_type = str(auth_type.value)
        self._login_id = login_id
        self._password = password
        self._http_session = aiohttp.ClientSession()
        self._broker = MirAIeBroker()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self._http_session.close()
        self._broker.disconnect()

    async def initialize(self):
        """Initializes the MirAIe API"""

        self._user = await self._login()
        self._home = await self._get_home_details()
        self._broker.set_topics(self._topics)
        self._broker.init_broker(self._home.home_id, self._user.access_token, self.reconnect_broker)
        self._broker.connect()

    def reconnect_broker(self, reconnect_callback: Callable):
        """Authenticates with MirAIe and reconnects to MQTT server with the new credentials"""
        loop = self._http_session.loop
        fut = asyncio.run_coroutine_threadsafe(self._login(), loop)

        self._user = fut.result()
        reconnect_callback(self._home.home_id, self._user.access_token)

    async def _login(self):
        data = {
            "clientId": HTTP_CLIENT_ID,
            "password": self._password,
            "scope": self._get_scope(),
        }

        data[self._auth_type] = self._login_id
        response = await self._http_session.post(LOGIN_URL, json=data)

        if response.status == 200:
            json = await response.json()
            return User(
                access_token=json["accessToken"],
                refresh_token=json["refreshToken"],
                user_id=json["userId"],
                expires_in=json["expiresIn"],
            )
        elif response.status == 401:
            raise AuthException("Authentication failed")
        elif response.status == 412:
            raise MobileNotRegisteredException(await response.json())
        else:
            raise ConnectionException(await response.json())

    async def _get_home_details(self):
        response = await self._http_session.get(
            HOMES_URL, headers=self._build_http_headers()
        )
        resp = await response.json()
        return await self._parse_home_details(resp[0])

    async def _parse_home_details(self, json_response):
        devices: list[Device] = []

        for space in json_response["spaces"]:
            space_name = space["spaceName"]
            for device in space["devices"]:
                device_id = device["deviceId"]
                topic = str(device["topic"][0])
                device_details = await self._get_device_details(device_id)

                category = str(device_details["category"]).lower()
                if category != "ac": continue

                device_status = await self._get_device_status(device_id)

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
                    broker=self._broker,
                    area_name=space_name,
                )

                self._topics.append(device.status_topic)
                self._topics.append(device.connection_status_topic)
                devices.append(device)

        return Home(home_id=json_response["homeId"], devices=devices)

    async def _get_device_details(self, device_id: str):
        url = f"{DEVICE_DETAILS_URL}/{device_id}"

        response = await self._http_session.get(
            url,
            headers=self._build_http_headers(),
        )

        json = await response.json()
        return json[0]

    async def _get_device_status(self, device_id: str):
        status: DeviceStatus

        response = await self._http_session.get(
            STATUS_URL.replace("{deviceId}", device_id),
            headers=self._build_http_headers(),
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

    def _build_http_headers(self):
        return {
            "Authorization": f"Bearer {self._user.access_token}"
            ,"Content-Type": "application/json",
        }

    def _get_scope(self):
        rnd = math.floor(random.random() * 1000000000)
        return f"an{str(rnd)}"
