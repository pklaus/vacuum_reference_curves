import serial
import time
from gauge_plugin import Gauge, GaugeError

class VacomMvc3(Gauge):

    def __init__(self, identifier='', channel=1):
        self.ser = serial.Serial(
            port=identifier,
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )

        self.read_command = b"RPV%d\r" % channel

    def get_reading(self):
        try:
            self.ser.write(self.read_command)
            time.sleep(.02)
            pressure = ''
            while self.ser.inWaiting() > 0:
                pressure += self.ser.read(1).decode('ascii')

            if pressure[0] == '0':
                pressure = float(pressure[3:-1])

                return {'pressure': pressure}
            pass
        except:
            raise GaugeError()
