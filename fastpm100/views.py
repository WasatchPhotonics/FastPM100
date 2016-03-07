""" GUI components for the demonstration program. Provides a bare bones
interface with a single button that changes the text to the current timestamp.
Used to demonstrate pytest-qt qtbot button clicking.  """

import pyqtgraph

from PySide import QtGui, QtCore

from .assets import strip_layout

import logging
log = logging.getLogger(__name__)

class StripWindow(QtGui.QMainWindow):
    """ Provide a standard gui control window with pyqtgraph for 3k per second
    visualizations.
    """
    def __init__(self, title="FastPM100"):
        log.debug("Init")
        super(StripWindow, self).__init__()

        self.ui = strip_layout.Ui_MainWindow()
        self.ui.setupUi(self)

        self.add_graph()
        self.create_signals()
        self.setGeometry(450, 250, 900, 400)

        app_icon = QtGui.QIcon(":ui/images/ApplicationIcon.ico")
        self.setWindowIcon(app_icon)
        self.setWindowTitle(title)
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
            """ Emit a signal for control upstream.
            """
            exit = QtCore.Signal(str)

        self.exit_signal = ViewClose()

    def closeEvent(self, event):
        """ Custom signal for controller to catch when the GUI close event is
        triggered by the user.
        """
        log.debug("View level close")
        self.exit_signal.exit.emit("close event")

class BlueGraphStripChart(QtGui.QMainWindow):
    """ Provide a standard gui control window with pyqtgraph for 3k per second
    visualizations.
    """
    def __init__(self):
        log.debug("Init")
        super(BlueGraphStripChart, self).__init__()

        self.ui = strip_layout.Ui_MainWindow()
        self.ui.setupUi(self)

        self.add_graph()
        self.create_signals()
        self.setGeometry(450, 250, 900, 400)

        app_icon = QtGui.QIcon(":ui/images/ApplicationIcon.ico")
        self.setWindowIcon(app_icon)
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
            """ Emit a signal for control upstream.
            """
            exit = QtCore.Signal(str)

        self.exit_signal = ViewClose()

    def closeEvent(self, event):
        """ Custom signal for controller to catch when the GUI close event is
        triggered by the user.
        """
        log.debug("View level close")
        self.exit_signal.exit.emit("close event")

class DualStripWindow(StripWindow):
    """ Like StripWindow, but pre-populate a second line plot with a right side
    axis.
    """
    def __init__(self, title="FastPM100"):
        log.debug("Init")
        super(DualStripWindow, self).__init__()

        self.updateViews()
        self.plot1.vb.sigResized.connect(self.updateViews)


    def add_graph(self):
        """ Add the pyqtgraph control to the stacked widget and make it
        viewable.
        """
        plot_widget = pyqtgraph.PlotWidget(name="dual")
        self.ui.plot = plot_widget

        self.plot1 = plot_widget.plotItem

        self.plot1.setLabels(left="axis 1")

        green_pen = "#1fd11f" # semi light-green
        red_pen = "#ff0000" # bold red
        plot_result = self.plot1.plot(range(3000), pen=green_pen)

        self.curve = plot_result

        self.plot2 = pyqtgraph.ViewBox()
        self.plot1.showAxis("right")
        self.plot1.scene().addItem(self.plot2)
        self.plot1.getAxis("right").linkToView(self.plot2)
        self.plot2.setXLink(self.plot1)
        self.plot1.getAxis("right").setLabel("axis 2", color=red_pen)

        self.curve_two = pyqtgraph.PlotCurveItem(range(2000), pen=red_pen)
        self.plot2.addItem(self.curve_two)

        self.ui.stackedWidget.addWidget(self.ui.plot)
        self.ui.stackedWidget.setCurrentIndex(2)


    def updateViews(self):
        """ Update the various plot item geometry according the the
        MultiplePlotAxes example to ensure the various axis line up.
        """
        self.plot2.setGeometry(self.plot1.vb.sceneBoundingRect())

        ## need to re-update linked axes since this was called
        ## incorrectly while views had different shapes.
        ## (probably this should be handled in ViewBox.resizeEvent)
        #p2.linkedViewChanged(p1.vb, p2.XAxis)
        self.plot2.linkedViewChanged(self.plot1.vb, self.plot2.XAxis)

