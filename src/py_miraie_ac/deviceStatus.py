"""Represents the status of a device"""
from py_miraie_ac.enums import DisplayState, FanMode, HVACMode, PowerMode, PresetMode, SwingMode

class DeviceStatus:
    """The Device Status class"""
    def __init__(
        self,
        is_online: bool,
        temperature: float,
        room_temp: float,
        power_mode: PowerMode,
        fan_mode: FanMode,
        swing_mode: SwingMode,
        display_state: DisplayState,
        hvac_mode: HVACMode,
        preset_mode: PresetMode,
    ):
        self.is_online = is_online
        self.temperature = temperature
        self.room_temp = room_temp
        self.power_mode = power_mode
        self.fan_mode = fan_mode
        self.swing_mode = swing_mode
        self.display_state = display_state
        self.hvac_mode = hvac_mode
        self.preset_mode = preset_mode
