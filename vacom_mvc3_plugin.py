import serial
import time
from gauge_plugin import Gauge, GaugeError

class VacomMvc3(Gauge):

    def __init__(self, identifier='', channels=(1,2,3)):
        self.ser = serial.Serial(
            port=identifier,
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        self.selected_channels = channels

    def get_readings(self):
        pressures = []
        for channel in self.selected_channels:
            pressures.append(self.get_reading(int(channel)))
        return {'pressures': pressures}

    def get_reading(self, channel):
        try:
            read_command = b"RPV%d\r" % channel
            self.ser.write(read_command)
            time.sleep(.03)
            pressure = ''
            while self.ser.inWaiting() > 0:
                pressure += self.ser.read(1).decode('ascii')

            if pressure[0] == '0':
                return float(pressure[3:-1])
            else:
                return float('nan')
        except:
            raise GaugeError()
