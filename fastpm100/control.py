""" Application level controller for demonstration program. Handles data model
and UI updates with MVC style architecture.
"""

import numpy
from PySide import QtCore

from collections import deque

from . import views, devices

import logging
log = logging.getLogger(__name__)

class Controller(object):
    def __init__(self, log_queue):
        log.debug("Control startup")

        # Create a separate process for the qt gui event loop
        #self.form = views.BasicWindow()
        self.form = views.StripWindow()

        self.create_data_model()
        self.create_signals()

        self.bind_view_signals()

        self.device = devices.SubProcessSimulatedPM100(log_queue)
        self.total_spectra = 0

        self.setup_main_event_loop()

    def create_data_model(self):
        """ Create data structures for application specific storage of reads.
        """
        self.history = deque()
        self.size = 3000
        #for item in range(self.size):
        #    self.history.append(0)

    def create_signals(self):
        """ Create signals for access by parent process.
        """
        class ControlClose(QtCore.QObject):
            exit = QtCore.Signal(str)

        self.control_exit_signal = ControlClose()

    def bind_view_signals(self):
        """ Connect GUI form signals to control events.
        """
        self.form.exit_signal.exit.connect(self.close)

    def setup_main_event_loop(self):
        """ Create a timer for a continuous event loop, trigger the start.
        """
        log.debug("Setup main event loop")
        self.continue_loop = True
        self.main_timer = QtCore.QTimer()
        self.main_timer.setSingleShot(True)
        self.main_timer.timeout.connect(self.event_loop)
        self.main_timer.start(0)

    def event_loop(self):
        """ Process queue events, interface events, then update views.
        """
        result = self.device.read()
        current = numpy.empty(0)
        while result is not None:
            current = numpy.append(current, result[1])
            result = self.device.read()

            #self.form.ui.labelCurrent.setText("%s" % result[1])
        #if len(self.history) > self.size:
            #self.history = self.history[-1:-3000]
        #log.debug("cur: %s" % current)
        self.form.curve.setData(current)

        if self.continue_loop:
            self.main_timer.start(0)

    def close(self):
        self.continue_loop = False
        self.device.close()
        log.debug("Control level close")
        self.control_exit_signal.exit.emit("Control level close")
