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
from enums import AuthType
from device import Device

async with MirAIeAPI(
        auth_type=AuthType.MOBILE, 
        login_id="YOUR_MOBILE_NUMBER", 
        password="YOUR_PASSWORD"
    ) as api:
    await api.initialize()
    for device in api.devices:
        print("Found device: ", device.friendly_name)
        device.set_temperature(24)
        device.turn_on()

asyncio.get_event_loop().run_until_complete(start())