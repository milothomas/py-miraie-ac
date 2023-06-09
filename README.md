# Python MirAIe AC API

An API to send commands and read the status of MirAIe air conditioners by Panasonic

**Installation**
```
pip install py-miraie-ac
```

**Usage**
```
import asyncio
from api import MirAIeAPI
from enums import AuthType, SwingMode
from device import Device

async with MirAIeAPI(auth_type=AuthType.MOBILE, login_id=mobile_number, password=password) as api:
        home:Home = await api.initialize()
        for deviceId, device in home.devices.items():
            print("Found device: ", device.friendly_name)
            officeAc.set_temperature(24)
            officeAc.turnOn()