#!/usr/bin/env python

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.Qt import Qt
import sys, copy

import matplotlib as mpl

from refcurves import get_refcurves_metadata

color_index = 0
def next_color():
    global color_index
    color = 'C%d' % (color_index % 10)
    color = mpl.colors.to_rgb(color)
    color = tuple(int(comp * 255) for comp in color)
    color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
    color_index += 1
    return color

def get_monospace_font():
    def is_fixed_pitch(font):
        return QtGui.QFontInfo(font).fixedPitch()
    font = QtGui.QFont("monospace")
    if is_fixed_pitch(font): return font
    font.setStyleHint(QtGui.QFont.Monospace)
    if is_fixed_pitch(font): return font
    font.setStyleHint(QtGui.QFont.TypeWriter)
    if is_fixed_pitch(font): return font
    font.setFamily("courier")
    if is_fixed_pitch(font): return font
    return font

class CheckboxTree(QtWidgets.QTreeWidget):
    """ https://stackoverflow.com/a/57820072/183995 """

    styles_changed_signal = QtCore.pyqtSignal()
    #checked_filenames_changed_signal = QtCore.pyqtSignal(str, str)
    checked_filenames_changed_signal = QtCore.pyqtSignal()
    checked_filenames = set()

    def __init__(self, data):
        super().__init__()
        self.setColumnCount(2)
        self.setHeaderLabels(['curve', 'color'])
        self.setColumnWidth(0, 600)
        self.setStyleSheet("QTreeWidget { font-size: 18; }")
        self.setIconSize(QtCore.QSize(32, 32))
        self.itemClicked.connect(self.click_handler)

        def add_subtree(element, parent=self, top_level=False):
            current = QtWidgets.QTreeWidgetItem(parent)
            if top_level: current.setExpanded(True)
            text = element['name']
            #if 'date' in element:
            #    text = element['date'] + ' - ' + text
            current.setText(0, text)
            if 'icon' in element:
                current.setIcon(0, QtGui.QIcon(element['icon']))
                #current.setData(0, Qt.DecorationRole, QtGui.QPixmap(element['icon']));
            if 'filename' in element:
                current.setData(0, Qt.UserRole, element['filename'])
                current.setText(1, next_color())
                current.setFont(1, get_monospace_font())
            if 'comment' in element:
                current.setToolTip(0, element['comment'])
            current.setFlags(current.flags() & ~Qt.ItemIsSelectable)
            current.setFlags(current.flags() | Qt.ItemIsUserCheckable)
            current.setCheckState(0, Qt.Unchecked)
            if 'children' in element:
                current.setFlags(current.flags() | Qt.ItemIsTristate)
                for child in element['children']:
                    add_subtree(child, parent=current)

        for element in data:
            add_subtree(element, top_level=True)

        #self.itemChanged['QTreeWidgetItem*'].connect(self.change_handler)
        self.itemChanged.connect(self.change_handler)

        self.update_styles()

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def change_handler(self, item, column):
        """ SLOT to handle change events on tree members """
        cf = copy.copy(self.checked_filenames)
        if column == 0:
            filename = item.data(0, Qt.UserRole)
            def update_selected_filenames(add=False, remove=False):
                if not filename: return
                try:
                    if add:
                        self.checked_filenames.add(filename)
                    if remove:
                        self.checked_filenames.remove(filename)
                except KeyError:
                    pass
            if item.checkState(0) == Qt.Checked:
                update_selected_filenames(add=True)
            elif item.checkState(0) == Qt.Unchecked:
                update_selected_filenames(remove=True)
            elif item.checkState(0) == Qt.PartiallyChecked:
                pass

        #with open('debug.log', 'a') as f:
        #    import time
        #    f.write("time: %s " % str(time.time()))
        #    f.write("item: %s " % str(item))
        #    f.write("column: %s " % str(column))
        #    f.write("filename: %s" % str(item.data(0, Qt.UserRole)))
        #    f.write("\n")

        if cf != self.checked_filenames:
            self.checked_filenames_changed_signal.emit()
        self.styles_changed_signal.emit()
        self.update_styles()

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def click_handler(self, item, column):
        """ SLOT to handle click events on tree members """
        if column != 1:
            return
        color = QtGui.QColorDialog.getColor()
        if color.isValid():
            item.setText(column, color.name())
            self.update_styles()

    def color_for_filename(self, filename):
        it = QtWidgets.QTreeWidgetItemIterator(self)
        while it.value():
            item = it.value()
            item_filename = item.data(0, Qt.UserRole)
            if item_filename == filename:
                color = item.text(1)
                color = QtGui.QColor(color)
                return color
            it += 1
        raise ValueError("filename %s not found in this CheckboxTree" % filename)

    def update_styles(self, item=None, column=None):

        def update_item(item):
            filename = item.data(0, Qt.UserRole)

            if filename:
                color = item.text(1)
                color = item.text(1)
                color = QtGui.QColor(color)
                item.setText(1, color.name())
                item.setForeground(1, color)

            def set_background(color):
                color = QtGui.QColor(color)
                for i in range(self.columnCount()):
                    item.setBackground(i, color)
                item.setBackground(0, color)

            def set_foreground(color):
                color = QtGui.QColor(color)
                item.setForeground(0, color)

            if item.checkState(0) == Qt.Checked:
                set_background("#ffffff")
                set_foreground('#000000')
            elif item.checkState(0) == Qt.Unchecked:
                set_background("#dddddd")
                set_foreground('#666666')
            elif item.checkState(0) == Qt.PartiallyChecked:
                set_background("#eeeeee")
                set_foreground('#333333')

        if item:
            update_item(item)
        else:
            it = QtWidgets.QTreeWidgetItemIterator(self)
            while it.value():
                update_item(it.value())
                it += 1
def main():
    app = QtWidgets.QApplication(sys.argv)
    tree = CheckboxTree(get_refcurves_metadata())
    tree.show()
    tree.resize(500, 300)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
