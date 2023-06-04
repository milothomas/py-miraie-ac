from enums import DisplayState, FanMode, HVACMode, PowerMode, PresetMode, SwingMode


class DeviceStatus:
    def __init__(
        self,
        isOnline: bool,
        temperature: float,
        roomTemp: float,
        powerMode: PowerMode,
        fanMode: FanMode,
        swingMode: SwingMode,
        displayState: DisplayState,
        hvacMode: HVACMode,
        presetMode: PresetMode,
    ):
        self.isOnline = isOnline
        self.temperature = temperature
        self.roomTemp = roomTemp
        self.powerMode = powerMode
        self.fanMode = fanMode
        self.swingMode = swingMode
        self.displayState = displayState
        self.hvacMode = hvacMode
        self.presetMode = presetMode
