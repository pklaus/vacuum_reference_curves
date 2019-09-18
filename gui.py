#!/usr/bin/env python

"""
PyQt5 code from:
http://zetcode.com/gui/pyqt5/widgets2/
https://www.walletfox.com/course/qtcheckablelist.php
"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QFrame,
    QSplitter, QStyleFactory, QApplication)
from PyQt5 import QtGui, QtCore
from PyQt5.Qt import Qt

from gui_list_reference_curves import CheckboxTree
from gui_vacuum_plot import VacuumPlot
from refcurves import get_refcurves_metadata, get_refcurve

import sys, time, copy

class ReferenceCurveGUI(QWidget):

    last_checked_filenames = None

    def __init__(self):
        super().__init__()

        self.initUI()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def initUI(self):

        data = get_refcurves_metadata()

        hbox = QHBoxLayout(self)

        self.ct = CheckboxTree(data)
        self.ct.checked_filenames_changed_signal.connect(self.update_plots_data)
        self.ct.styles_changed_signal.connect(self.update_plots_style)

        topleft = self.ct
        topleft.setFrameShape(QFrame.StyledPanel)

        topright = QFrame(self)
        topright.setFrameShape(QFrame.StyledPanel)

        self.vp = VacuumPlot(title='Vacuum Plot', name='Vacuum')
        self.vp.enableCrosshair()

        bottom = self.vp
        bottom.setFrameShape(QFrame.StyledPanel)

        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(topleft)
        splitter1.addWidget(topright)

        splitter2 = QSplitter(Qt.Vertical)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(bottom)

        hbox.addWidget(splitter2)
        self.setLayout(hbox)

        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle('UFO Vacuum Reference Curves')
        self.resize(1700, 1000)
        self.showMaximized()

    def update_plots_style(self):
        for filename in self.ct.checked_filenames:
            color = self.ct.color_for_filename(filename)
            self.vp.set_color(filename, c=color)

    def update_plots_data(self):
        # run only if selected curves has changed
        if self.ct.checked_filenames == self.last_checked_filenames:
            return
        self.last_checked_filenames = copy.copy(self.ct.checked_filenames)

        for filename in self.ct.checked_filenames:
            rc = get_refcurve(filename)
            color = self.ct.color_for_filename(filename)
            self.vp.show_data(filename, rc=rc, c=color)
        self.vp.remove_all_but(self.ct.checked_filenames)
        #self.vp.setXRange(0., 10.)
        #self.vp.draw_start()
        #self.vp.save_as('exported_chart.png', width=1920)

    def live_plot(self, source):
        return
        ### Start a timer to rapidly update the plot in pw
        #t = QtCore.QTimer()
        #t.timeout.connect(updateData)
        #t.start(50)
        #updateData()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = ReferenceCurveGUI()

    # keep Python in the loop in order to be able to press Ctrl-c
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(1)

    sys.exit(app.exec_())
