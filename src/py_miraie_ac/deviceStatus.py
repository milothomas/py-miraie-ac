"""Represents the status of a device"""
from .enums import DisplayState, FanMode, HVACMode, PowerMode, PresetMode, SwingMode

class DeviceStatus:
    """The Device Status class"""
    def __init__(
        self,
        is_online: bool,
        temperature: float,
        room_temp: float,
        power_mode: PowerMode,
        fan_mode: FanMode,
        display_state: DisplayState,
        hvac_mode: HVACMode,
        preset_mode: PresetMode,
        horizontal_swing_mode: SwingMode,
        vertical_swing_mode: SwingMode,
    ):
        self.is_online = is_online
        self.temperature = temperature
        self.room_temp = room_temp
        self.power_mode = power_mode
        self.fan_mode = fan_mode
        self.display_state = display_state
        self.hvac_mode = hvac_mode
        self.preset_mode = preset_mode
        self.horizontal_swing_mode = horizontal_swing_mode
        self.vertical_swing_mode = vertical_swing_mode
        