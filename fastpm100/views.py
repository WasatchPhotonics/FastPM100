""" GUI components for the FastPM100 application.
"""

import logging

from PySide import QtGui, QtSvg, QtCore


log = logging.getLogger(__name__)

class SingleNumber(QtGui.QMainWindow):
    """ Provie a bare form layout with a single number.
    """
    def __init__(self, parent=None):
        log.debug("Init of %s", self.__class__.__name__)
        super(SingleNumber, self).__init__(parent)
        self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.vbox = QtGui.QVBoxLayout()
        self.main_widget = QtGui.QWidget()
        self.main_widget.setLayout(self.vbox)
        self.central_widget.addWidget(self.main_widget)

        self.lbl_info = QtGui.QLabel("FastPM100")
        self.vbox.addWidget(self.lbl_info)

        self.button = QtGui.QPushButton("Change Text")
        self.vbox.addWidget(self.button)

        self.button.clicked.connect(self.change_text)

        self.setGeometry(30, 30, 640, 500)
        self.show()

    def change_text(self):
        log.debug("change text")
        self.lbl_info.setText("Button clicked")
