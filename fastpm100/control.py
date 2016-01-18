""" Application level controller for demonstration program. Handles data model
and UI updates with MVC style architecture.
"""
import time
import numpy
from PySide import QtCore

from collections import deque

from . import views, wrapper

import logging
log = logging.getLogger(__name__)

class Controller(object):
    def __init__(self, log_queue):
        log.debug("Control startup")

        # Create a separate process for the qt gui event loop
        self.form = views.StripWindow()

        self.create_data_model()
        self.create_signals()

        self.bind_view_signals()

        delay_time = 0.1
        self.device = wrapper.SubProcess(log_queue,
                                         delay_time=delay_time)
        self.total_spectra = 0

        self.setup_main_event_loop()

    def create_data_model(self):
        """ Create data structures for application specific storage of reads.
        """
        self.history = deque()
        self.size = 300
        self.current = numpy.empty(0)
        self.array_full = False

        # Instantaneous performance counters
        self.start_time = time.time()
        self.read_frames = 0
        self.reported_frames = 0

        # Per second performance counters
        self.second_time = time.time()
        self.total_rend = 0
        self.last_reported = 0
        self.last_rend = 0

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
        if result is not None:

            self.read_frames += 1
            self.current = numpy.append(self.current, result[1])
            self.reported_frames = result[0]

            if len(self.current) >= self.size:
                self.current = numpy.roll(self.current, -1)
                self.current = self.current[0:self.size]

            self.form.curve.setData(self.current)


            if len(self.current) > 0:
                self.form.ui.labelMinimum.setText("%s" % numpy.min(self.current))
                self.form.ui.labelMaximum.setText("%s" % numpy.max(self.current))

        self.update_performance_metrics()

        self.total_rend += 1

        if self.continue_loop:
            self.main_timer.start(0)

    def update_performance_metrics(self):
        """ Compute the data frames per second and render frames per second,
        update the main interface.  """

        # Total number of frames read, ms per frame instantaneous performance
        # display
        time_diff = time.time() - self.start_time
        display_str = "%s, %0.3fms" % (self.read_frames, time_diff)
        self.form.ui.labelCurrent.setText("%s" % display_str)


        # Show the total number of data frames collected per second, as well as
        # the number of rend events per second
        second_diff = time.time() - self.second_time
        if second_diff >= 1.0:

            data_per_second = self.reported_frames - self.last_reported
            rend_per_second = self.total_rend - self.last_rend
            skip_per_second = data_per_second - rend_per_second
            if skip_per_second < 0:
                skip_per_second = 0

            sfu = self.form.ui
            sfu.labelDataFPS.setText("%s" % data_per_second)
            sfu.labelRenderFPS.setText("%s" % rend_per_second)
            sfu.labelSkipFPS.setText("%s" % skip_per_second)

            self.second_time = time.time()
            self.last_reported = self.reported_frames
            self.last_rend = self.total_rend


        self.start_time = time.time()

    def close(self):
        self.continue_loop = False
        self.device.close()
        log.debug("Control level close")
        self.control_exit_signal.exit.emit("Control level close")
