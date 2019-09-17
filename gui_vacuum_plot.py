import PyQt5
from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from datetime import datetime as dt

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

def format_timedelta(seconds):
    return str(dt.utcfromtimestamp(seconds) - dt.utcfromtimestamp(0))

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autoSIPrefix = False

    def tickStrings(self, values, scale, spacing):
        return [format_timedelta(value) for value in values]
        # PySide's QTime() initialiser fails miserably and dismisses args/kwargs

    def tickSpacing(self, minVal, maxVal, size):
        """
        http://www.pyqtgraph.org/documentation/_modules/pyqtgraph/graphicsItems/AxisItem.html#AxisItem.tickSpacing
        """
        seconds_difference = maxVal - minVal
        if seconds_difference < 10:
            return [ (1, 0), (1, 0) ]
        elif seconds_difference < 60:
            return [ (30, 0), (5, 0) ]
        elif seconds_difference < 500:
            return [ (60, 0), (10, 0) ]
        elif seconds_difference < 3500:
            return [ (15*60, 0), (60, 0) ]
        elif seconds_difference < 11*3600:
            return [ (3600, 0), (15*60, 0) ]
        elif seconds_difference < 23*3600:
            return [ (12*3600, 0), (3600, 0) ]
        elif seconds_difference < 6*24*3600:
            return [ (24*3600, 0), (6*3600, 0) ]
        elif seconds_difference < 13*24*3600:
            return [ (7*24*3600, 0), (24*3600, 0) ]
        elif seconds_difference < 170*24*3600:
            return [ (28*24*3600, 0), (7*24*3600, 0) ]
        elif seconds_difference < 360*24*3600:
            return [ (180*24*3600, 0), (7*24*3600, 0) ]
        else:
            return [ (365*24*3600, 0), (28*24*3600, 0) ]

class VacuumPlot(pg.PlotWidget):
    """
    influenced by
    https://github.com/pyqtgraph/pyqtgraph/blob/develop/examples/PlotWidget.py
    """

    current_plots = {}

    def __init__(self, *args, **kwargs):

        kwargs['axisItems'] = {'bottom': TimeAxisItem(orientation='bottom')}

        super().__init__(*args, **kwargs)

        self.setLogMode(y=True)
        self.showGrid(x=True, y=True, alpha=0.2)

        self.setLabel('left', 'pressure', units='mbar')
        self.setLabel('bottom', 'Time since start of pumping', units='h:mm:ss')

    def show_data(self, id, rc=None, c=(200, 200, 100)):
        #if id in self.current_plots: plot = self.current_plots[id]
        #else: plot = self.plot()
        plot = self.current_plots.get(id, self.plot())
        self.current_plots[id] = plot
        plot.setPen(width=3, color=c)
        xd = [(ts-rc.start) for ts in rc.data[0]]
        yd = rc.data[1]
        plot.setData(y=yd, x=xd)

    def set_color(self, id, c=(200, 200, 100)):
        plot = self.current_plots.get(id, None)
        if not plot:
            #raise KeyError('No plot with id %s found' % id)
            return
        plot.setPen(width=3, color=c)

    def draw_start(self):
        ### Add in some extra graphics
        x_0 = -0.01
        x_w = 0.02
        y_0 = np.log10(0.001)
        y_w = np.log10(1013) - y_0
        rect = QtGui.QGraphicsRectItem(QtCore.QRectF(x_0, y_0, x_w, y_w))
        rect.setPen(pg.mkPen(100, 200, 100))
        self.addItem(rect)

    def remove_all_but(self, but):
        ready_for_deletion = []
        for id in self.current_plots:
            if id not in but:
                self.removeItem(self.current_plots[id])
                ready_for_deletion.append(id)
        for id in ready_for_deletion:
            del self.current_plots[id]
