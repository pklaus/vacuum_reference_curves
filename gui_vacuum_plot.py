import PyQt5
from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np
from datetime import datetime as dt, timedelta

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

def format_timedelta(seconds):
    td = dt.utcfromtimestamp(seconds) - dt.utcfromtimestamp(0)
    if td >= timedelta(0):
        ret_str = str(td)
    else:
        ret_str = '-' + str(-td)
    if ret_str.endswith(('day, 0:00:00', 'days, 0:00:00')):
        ret_str = ret_str[:-9]
    return ret_str

class Crosshair(pg.GraphicsObject):

    def __init__(self, pen=None):
        pg.GraphicsObject.__init__(self)
        self.pos = QtCore.QPoint(0, 0)
        self.pen = pen or mkPen('ff0', 0.5)
        self.gap = 20 # gap in pixels

    def boundingRect(self):
        br = self.viewRect()
        return br.normalized()

    def paint(self, p, *args):
        br = self.boundingRect()
        px_width, px_height = self.pixelSize()
        p.setPen(self.pen)
        gap = px_width * self.gap
        p.drawLine(pg.Point(br.left(), self.pos.y()), pg.Point(self.pos.x() - gap/2, self.pos.y()))
        p.drawLine(pg.Point(self.pos.x() + gap/2, self.pos.y()), pg.Point(br.right(), self.pos.y()))
        gap = px_height * self.gap
        p.drawLine(pg.Point(self.pos.x(), br.top()), pg.Point(self.pos.x(), self.pos.y() - gap/2))
        p.drawLine(pg.Point(self.pos.x(), self.pos.y() + gap/2), pg.Point(self.pos.x(), br.bottom()))

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
        if   seconds_difference < 5:
            return [ (1, 0), (0.2, 0) ]
        elif seconds_difference < 10:
            return [ (5, 0), (1, 0) ]
        elif seconds_difference < 60:
            return [ (30, 0), (5, 0) ]
        elif seconds_difference < 400:
            return [ (60, 0), (10, 0) ]
        elif seconds_difference < 1000:
            return [ (5*60, 0), (60, 0) ]
        elif seconds_difference < 3500:
            return [ (15*60, 0), (5*60, 0) ]
        elif seconds_difference < 18*3600:
            return [ (3600, 0), (15*60, 0) ]
        elif seconds_difference < 40*3600:
            return [ (12*3600, 0), (3*3600, 0) ]
        elif seconds_difference < 12*24*3600:
            return [ (24*3600, 0), (6*3600, 0) ]
        elif seconds_difference < 22*24*3600:
            return [ (7*24*3600, 0), (24*3600, 0) ]
        elif seconds_difference < 50*24*3600:
            return [ (14*24*3600, 0), (7*24*3600, 0) ]
        elif seconds_difference < 170*24*3600:
            return [ (28*24*3600, 0), (7*24*3600, 0) ]
        elif seconds_difference < 250*24*3600:
            return [ (28*24*3600, 0), (14*24*3600, 0) ]
        elif seconds_difference < 500*24*3600:
            return [ (56*24*3600, 0), (28*24*3600, 0) ]
        elif seconds_difference < 2*360*24*3600:
            return [ (112*24*3600, 0), (56*24*3600, 0) ]
        elif seconds_difference < 20*360*24*3600:
            return [ (365*24*3600, 0), (365/12*24*3600, 0) ]
        else:
            return [ (3650*24*3600, 0), (365*24*3600, 0) ]

class VacuumPlot(pg.PlotWidget):
    """
    influenced by
    https://github.com/pyqtgraph/pyqtgraph/blob/develop/examples/PlotWidget.py
    """

    current_plots = {}
    _crosshair_enabled = False
    _mouse_over_plot = False

    def __init__(self, *args, crosshair=False, **kwargs):


        pg.setConfigOptions(antialias=True)
        kwargs['axisItems'] = {'bottom': TimeAxisItem(orientation='bottom')}

        self.default_title = kwargs.get('title', '')

        super().__init__(*args, **kwargs)

        self.setLogMode(y=True)
        self.getAxis('left').enableAutoSIPrefix(enable=False)
        self.showGrid(x=True, y=True, alpha=0.4)

        # http://www.pyqtgraph.org/documentation/graphicsItems/viewbox.html#pyqtgraph.ViewBox.setLimits
        limits = {
          'xMin': -100*360*24*3600,
          'xMax':  100*360*24*3600,
          'yMin': np.log10(1e-100),
          'yMax': np.log10(1e100),
          'minXRange': 0.2,
          #'maxXRange': ,
          #'minYRange': ,
          #'maxYRange': ,
        }
        self.setLimits(**limits)

        self.setLabel('left', 'pressure', units='mbar')
        self.setLabel('bottom', 'Time since start of pumping', units='h:mm:ss')

        if crosshair:
            self.enableCrosshair()
        self.setMouseTracking(True)
        self.scene().sigMouseMoved.connect(self.mouseMoved)

        # fix to repaint formerly protruding axis tick labels
        self.sigRangeChanged.connect(self.forceRepaint)

    def enableCrosshair(self):
        self._crosshair_enabled = True
        pen = pg.mkPen('000', width=0.5)
        self._crosshair = Crosshair(pen=pen)
        self.addItem(self._crosshair, ignoreBounds=True)
        self.hideCrosshair() # only show once mouse is moving

    def showCrosshair(self):
        self._crosshair.show()

    def hideCrosshair(self):
        self._crosshair.hide()

    def mouseMoved(self, evt):
        pos = evt
        if self.plotItem.getViewBox().geometry().contains(pos):
            mousePoint = self.plotItem.vb.mapSceneToView(pos)
            x = format_timedelta(round(mousePoint.x()))
            #y = mousePoint.y()
            #y = np.log10(mousePoint.y())
            y = 10**mousePoint.y()
            self.plotItem.setTitle(f"<span style='font-size: 15pt'>pressure: {y:.2e} mbar, time: {x}, </span>")
            if not self._mouse_over_plot:
                # entering the plot for the first time
                self._mouse_over_plot = True
                if self._crosshair_enabled:
                    self.showCrosshair()
                    cursor = QtGui.QCursor(QtCore.Qt.BlankCursor)
                    QtGui.QApplication.setOverrideCursor(cursor)
                    QtGui.QApplication.changeOverrideCursor(cursor)
                #QtGui.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
            if self._crosshair_enabled:
                self._crosshair.pos = mousePoint
                self.forceRepaint()
        else:
            self.mouseLeftTargetArea()

    def mouseLeftTargetArea(self):
        if not self._mouse_over_plot:
            # this method should be called only once when the mouse leaves the target region (ViewBox)
            return
        self._mouse_over_plot = False
        self.plotItem.setTitle(self.default_title)
        if self._crosshair_enabled:
            self.hideCrosshair()
            QtGui.QApplication.restoreOverrideCursor()

    def leaveEvent(self, event):
        self.mouseLeftTargetArea()
        return super().leaveEvent(event)

    def forceRepaint(self, *args, **kwargs):
        self.viewport().update()

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

    def save_as(self, filename, width=200):
        """ http://www.pyqtgraph.org/documentation/exporting.html """
        exporter = pg.exporters.ImageExporter(self.plotItem)
        exporter.parameters()['width'] = width # this also affects the height parameter
        exporter.export(filename)

def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    vp = VacuumPlot()
    vp.enableCrosshair()
    vp.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
