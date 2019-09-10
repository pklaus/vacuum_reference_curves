from labjack import ljm
from balzerspkg020_helpers import interpolate_log_aware
from balzerspkg020 import tables

from gauge_plugin import Gauge, GaugeError

class BalzersPkg020(Gauge):

    def __init__(self, identifier=''):
        self.handle = ljm.openS("ANY", "ANY", "ANY")

    def get_reading(self):
        try:
            voltage = ljm.eReadName(self.handle, "AIN0")
        except ljm.ljm.LJMError:
            raise GaugeError()
        pressure = interpolate_log_aware(voltage, tables['tpr2'])
        return {'pressure': pressure, 'voltage': voltage}
