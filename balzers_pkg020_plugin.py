from labjack import ljm
from balzerspkg020_helpers import interpolate_log_aware
from balzerspkg020 import tables

from gauge_plugin import Gauge, GaugeError

class BalzersPkg020(Gauge):

    def __init__(self, identifier='', channels=('AIN0',)):
        self.handle = ljm.openS("ANY", "ANY", "ANY")
        self.selected_channels = channels

    def get_readings(self):
        pressures = []
        voltages = []
        for channel in self.selected_channels:
            reading = self.get_reading(channel)
            pressures.append(reading['pressure'])
            voltages.append(reading['voltage'])
        return {'pressures': pressures, 'voltages': voltages}

    def get_reading(self, channel):
        try:
            voltage = ljm.eReadName(self.handle, "AIN0")
        except ljm.ljm.LJMError:
            raise GaugeError()
        pressure = interpolate_log_aware(voltage, tables['tpr2'])
        return {'pressure': pressure, 'voltage': voltage}
