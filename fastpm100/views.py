""" GUI components for the demonstration program. Provides a bare bones
interface with a single button that changes the text to the current timestamp.
Used to demonstrate pytest-qt qtbot button clicking.  """
import datetime

from PySide import QtGui, QtCore

from .assets import resources_rc

import logging
log = logging.getLogger(__name__)

class BasicWindow(QtGui.QMainWindow):
    """ Provie a bare form layout with basic interactivity.
    """
    def __init__(self, parent=None):
        log.debug("Init of %s" % self.__class__.__name__)
        super(BasicWindow, self).__init__(parent)

        # The main widget. Certain implementations will still create a
        # form with the geometry specified below. Enforce the central
        # widget for better portability.
        self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.vbox = QtGui.QVBoxLayout()
        self.main_widget = QtGui.QWidget()
        self.main_widget.setLayout(self.vbox)
        self.central_widget.addWidget(self.main_widget)

        self.lbl_logo = QtGui.QLabel()
        logo_filename = ":ui/images/wp_logo.png"
        self.lbl_logo.setPixmap(QtGui.QPixmap(logo_filename))
        self.vbox.addWidget(self.lbl_logo)

        self.lbl_info = QtGui.QLabel("Application Default")
        self.vbox.addWidget(self.lbl_info)

        self.button = QtGui.QPushButton("Change Text")
        self.vbox.addWidget(self.button)

        self.txt_box = QtGui.QTextEdit("Event text area")
        self.vbox.addWidget(self.txt_box)

        self.create_signals()

        self.setGeometry(30, 30, 400, 400)
        self.show()
        app_icon = QtGui.QIcon(":ui/images/ApplicationIcon.ico")
        self.setWindowIcon(app_icon)


    def change_text(self):
        new_txt = "Button clicked: %s" % datetime.datetime.now()
        self.lbl_info.setText(new_txt)
        log.debug(new_txt)
        print "post log debug STDOUT: %s" % new_txt

    def create_signals(self):
        """ Create signal objects to be used by controller and internal simple
        events.
        """
        self.button.clicked.connect(self.change_text)

        class ViewClose(QtCore.QObject):
            exit = QtCore.Signal(str)

        self.exit_signal = ViewClose()

    def closeEvent(self, event):
        """ Custom signal for controller to catch when the GUI close event is
        triggered by the user.
        """
        log.debug("View level close")
        self.exit_signal.exit.emit("close event")
