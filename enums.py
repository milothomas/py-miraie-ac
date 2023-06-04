from enum import Enum


class AuthType(Enum):
    Mobile = "mobile"
    Email = "email"
    Username = "username"


class DisplayState(Enum):
    ON = "on"
    OFF = "off"


class FanMode(Enum):
    AUTO = "auto"
    QUIET = "quiet"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HVACMode(Enum):
    COOL = "cool"
    AUTO = "auto"
    DRY = "dry"
    FAN = "fan"

class PowerMode(Enum):
    ON = "on"
    OFF = "off"


class PresetMode(Enum):
    NONE = "none"
    ECO = "eco"
    BOOST = "boost"


class SwingMode(Enum):
    AUTO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5