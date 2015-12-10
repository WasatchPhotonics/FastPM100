""" GUI components for the FastPM100 application.
"""

import sys

from PySide import QtGui, QtSvg, QtCore


class SingleNumber(QtGui.QMainWindow):
    """ Provie a bare form layout with a single number.
    """
    def __init__(self, parent=None):
        super(SingleNumber, self).__init__(parent)
        self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.vbox = QtGui.QVBoxLayout()
        self.main_widget = QtGui.QWidget()
        self.main_widget.setLayout(self.vbox)
        self.central_widget.addWidget(self.main_widget)

        self.lbl_info = QtGui.QLabel("FastPM100")
        self.vbox.addWidget(self.lbl_info)

        self.setGeometry(30, 30, 640, 480)
        self.show()
