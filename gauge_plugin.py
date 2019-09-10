
class GaugeError(Exception):
    pass

class Gauge:

    def __init__(self, identifier=''):
        raise NotImplementedError()

    def get_reading(self):
        """ returns pressure in mbar """
        raise NotImplementedError()
