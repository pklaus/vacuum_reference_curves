import PyQt5
from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class VacuumPlot(pg.PlotWidget):
    """
    influenced by
    https://github.com/pyqtgraph/pyqtgraph/blob/develop/examples/PlotWidget.py
    """

    current_plots = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setLogMode(y=True)
        self.showGrid(x=True, y=True, alpha=0.2)

        self.setLabel('left', 'pressure', units='mbar')
        self.setLabel('bottom', 'Time', units='h')

    def show_data(self, id, rc=None, c=(200, 200, 100)):
        #if id in self.current_plots: plot = self.current_plots[id]
        #else: plot = self.plot()
        plot = self.current_plots.get(id, self.plot())
        self.current_plots[id] = plot
        plot.setPen(width=3, color=c)
        xd = [(ts-rc.start) / 3600 for ts in rc.data[0]]
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
