""" GUI components for the demonstration program. Provides a bare bones
interface with a single button that changes the text to the current timestamp.
Used to demonstrate pytest-qt qtbot button clicking.  """
import datetime

import pyqtgraph

from PySide import QtGui, QtCore

from .assets import resources_rc

from .assets import strip_layout

import logging
log = logging.getLogger(__name__)

class StripWindow(QtGui.QMainWindow):
    """ Provide a standard gui control window with pyqtgraph for 3k per second
    visualizations.
    """
    def __init__(self):
        log.debug("Init of %s" % self.__class__.__name__)
        super(StripWindow, self).__init__()

        self.ui = strip_layout.Ui_MainWindow()
        self.ui.setupUi(self)

        self.add_graph()
        self.create_signals()
        self.setGeometry(450, 250, 1080, 300)

        self.show()

    def add_graph(self):
        """ Add the pyqtgraph control to the stacked widget and make it
        viewable.
        """
        self.ui.plot = pyqtgraph.PlotWidget(name="mystery")

        green_pen = "#1fd11f" # semi light-green

        self.curve = self.ui.plot.plot(range(3000), pen=green_pen)

        self.ui.stackedWidget.addWidget(self.ui.plot)
        self.ui.stackedWidget.setCurrentIndex(2)

    def create_signals(self):
        """ Create signal objects to be used by controller and internal simple
        events.
        """
        class ViewClose(QtCore.QObject):
            exit = QtCore.Signal(str)

        self.exit_signal = ViewClose()

    def closeEvent(self, event):
        """ Custom signal for controller to catch when the GUI close event is
        triggered by the user.
        """
        log.debug("View level close")
        self.exit_signal.exit.emit("close event")
