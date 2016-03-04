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
    """ Control portion of the MVC design pattern. Creates a data mode, a view,
    and links the required signals. This is designed to be run by both the main
    user script as well as the test_control.
    """
    def __init__(self, log_queue, device_name="SimulatedPM100",
                 history_size=30, title="FastPM100"):
        log.debug("Control startup")

        # A value of zero means update as fast as possible
        self.update_time_interval = 0

        # Create a separate process for the qt gui event loop
        self.form = views.StripWindow(title=title)

        self.create_data_model(history_size)
        self.create_signals()

        self.bind_view_signals()

        delay_time = None
        self.device = wrapper.SubProcess(log_queue,
                                         delay_time=delay_time,
                                         device_name=device_name)
        self.total_spectra = 0

        self.form.ui.actionContinue.setChecked(True)

        self.setup_main_event_loop()

    def create_data_model(self, history_size):
        """ Create data structures for application specific storage of reads.
        """
        self.history = deque()
        self.size = history_size
        self.current = numpy.empty(0)
        self.array_full = False

        # Instantaneous performance counters
        self.start_time = time.time()
        # total non-none acquisitions from data process
        self.read_frames = 0
        # last acquisition number as reported from data process
        self.reported_frames = 0

        # Per second performance counters
        self.second_time = time.time()
        self.total_rend = 0
        self.last_reported = 0
        self.last_rend = 0

        self.live_updates = True

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

        self.form.ui.actionPause.triggered[bool].connect(self.on_pause)
        self.form.ui.actionContinue.triggered[bool].connect(self.on_continue)

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
            self.reported_frames = result[0]

            if len(self.current) >= self.size:
                self.current = numpy.roll(self.current, -1)
                self.current[-1] = result[1]
            else:
                self.current = numpy.append(self.current, result[1])

        self.render_graph()

        self.update_performance_metrics()

        if self.continue_loop:
            self.main_timer.start(self.update_time_interval)

    def render_graph(self):
        """ Update the graph data, indicate minimum and maximum values.
        """
        if not self.live_updates:
            return

        self.form.curve.setData(self.current)

        if len(self.current) > 0:
            min_text = "%0.3f mw" % numpy.min(self.current)
            max_text = "%0.3f mw" % numpy.max(self.current)
            self.form.ui.labelMinimum.setText(min_text)
            self.form.ui.labelMaximum.setText(max_text)

        self.total_rend += 1

    def update_performance_metrics(self):
        """ Compute the data frames per second and render frames per second,
        update the main interface.  """

        # Total number of frames read, ms per frame instantaneous performance
        # display
        time_diff = time.time() - self.start_time
        display_str = "%0.3fms" % (time_diff)
        self.form.ui.labelCurrent.setText("%s" % display_str)


        # Show the total number of data frames collected per second, as well as
        # the number of rend events per second
        second_diff = time.time() - self.second_time
        if second_diff >= 1.0:

            data_per_second = self.reported_frames - self.last_reported
            rend_per_second = self.total_rend - self.last_rend
            skip_per_second = data_per_second - rend_per_second

            sfu = self.form.ui
            sfu.labelDataFPS.setText("%s" % data_per_second)
            sfu.labelRenderFPS.setText("%s" % rend_per_second)
            sfu.labelSkipFPS.setText("%s" % skip_per_second)

            self.second_time = time.time()
            self.last_reported = self.reported_frames
            self.last_rend = self.total_rend


        self.start_time = time.time()

    def close(self):
        """ Issue control commands to the sub process device, as well as the qt
        view.  """
        self.continue_loop = False
        self.device.close()
        log.debug("Control level close")
        self.control_exit_signal.exit.emit("Control level close")

    def on_continue(self, action):
        """ Continue and pause buttons are the equivalent of toggle buttons.
        Only one can be enabled at a time.
        """
        log.info("Continue live updates")
        if action == False:
            self.form.ui.actionContinue.setChecked(True)

        self.form.ui.actionPause.setChecked(False)
        self.live_updates = True

    def on_pause(self, action):
        """ Continue and pause buttons are the equivalent of toggle buttons.
        Only one can be enabled at a time.
        """
        log.info("Pause live updates: %s", action)
        if action == False:
            self.form.ui.actionPause.setChecked(True)

        self.form.ui.actionContinue.setChecked(False)
        self.live_updates = False


class DayGroupController(Controller):
    def __init__(self, *args, **kwargs):
        super(DayGroupController, self).__init__(*args, **kwargs)

        # ms to update the main interface to control the quantity of
        # data displayed. Update once every 10 seconds for an entire 24
        # hour period
        self.update_time_interval = 10000

class ForeverController(Controller):
    def __init__(self, *args, **kwargs):
        super(ForeverController, self).__init__(*args, **kwargs)

        self.update_time_interval = 60000
