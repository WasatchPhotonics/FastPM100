""" Application level controller for demonstration program. Handles data model
and UI updates with MVC style architecture.
"""
import csv
import time
import numpy
import random
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
                 history_size=30, title="FastPM100",
                 geometry=[200, 200, 600, 600],
                 filename=None,
                 update_time_interval=0):
        log.debug("Control startup")

        self.history_size = history_size
        self.title = title
        self.geometry = geometry
        self.filename = filename

        # A value of zero means update as fast as possible
        self.update_time_interval = update_time_interval

        # Create a separate process for the qt gui event loop
        self.form = views.StripWindow(title=self.title)

        self.create_data_model(self.history_size)
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

            #log.debug("raw frame: %s", result)
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


class DualController(Controller):
    """ Like Controller above, but use the dual update view.
    """
    def __init__(self, *args, **kwargs):
        super(DualController, self).__init__(*args, **kwargs)
        log.debug("Dual Control startup")

        self.form = views.DualStripWindow(title=self.title)

        # Create numpy array for holding second set of data
        self.second = numpy.empty(0)

        # The form was already created in Controller, after it has been
        # recreated as a dual strip window above, re-bind all of the signals.
        self.create_signals()

        self.bind_view_signals()

        self.form.ui.actionContinue.setChecked(True)

    def event_loop(self):
        """ Process queue events, interface events, then update views.
        """

        result = self.device.read()
        # ltemp, power
        if result is not None:
            #print "raw result: ", result

            self.read_frames += 1
            self.reported_frames = result[0]

            if len(self.current) >= self.size:
                self.current = numpy.roll(self.current, -1)
                self.second = numpy.roll(self.second, -1)
                self.current[-1] = result[1][1]
                self.second[-1] = result[1][0]
            else:
                self.current = numpy.append(self.current, result[1][1])
                self.second = numpy.append(self.second, result[1][0])

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
        self.form.curve_two.setData(self.second)

        if len(self.current) > 0:
            min_text = "%0.3f mw" % numpy.min(self.current)
            max_text = "%0.3f mw" % numpy.max(self.current)
            self.form.ui.labelMinimum.setText(min_text)
            self.form.ui.labelMaximum.setText(max_text)

        self.total_rend += 1


class AllController(Controller):
    """ Like Controller above, but use the all data display view and
    update the control logic to display all data points.
    """
    def __init__(self, *args, **kwargs):
        super(AllController, self).__init__(*args, **kwargs)
        log.debug("All Control startup: %s", self.title)

        self.form = views.AllStripWindow(title=self.title,
                                         geometry=self.geometry)

        self.create_data_sources()

        # The form was already created in Controller, after it has been
        # recreated as a dual strip window above, re-bind all of the signals.
        self.create_signals()

        self.bind_view_signals()
        self.bind_custom_actions()

        self.form.ui.actionContinue.setChecked(True)
        self.form.ui.actionCCD_Temp.setChecked(True)
        self.form.ui.actionLaser_Temp.setChecked(True)
        self.form.ui.actionLaser_Power.setChecked(True)
        self.form.ui.actionYellow_Therm.setChecked(True)
        self.form.ui.actionBlue_Therm.setChecked(True)
        self.form.ui.actionAmps.setChecked(True)

        if self.filename != None:
            self.preload_csv(self.filename, self.update_time_interval,
                             self.history_size)

            log.debug("Setup interface update timer")
            self.update_history_timer = QtCore.QTimer()
            self.update_history_timer.setSingleShot(True)
            self.update_history_timer.timeout.connect(self.update_history)

            log.info("Update interface with averages over %s",
                     self.update_time_interval)
            self.update_history_timer.start(self.update_time_interval)

        self.render_graph()

    def preload_csv(self, filename, interval, size):
        """ Assumes csv file is update every 10 seconds.
        """
        log.info("Attempting to open: %s", filename)

        # if 10 second gaps for 1 day:
        # read every entry, if total size of temp arr is greater than 8640
        # slice off the last 8640, put in current array
        total_rows = 0
        with open(filename) as csv_file:
            combined_reader = csv.DictReader(csv_file, delimiter=",")
            for row in combined_reader:

                # Smooth graphs with average
                self.hist_assign(row, name="Average")
                total_rows += 1

        log.info("Read %s rows ", total_rows)

        # Assumes that if you specify 8640 10 second readings, you want one day
        # of data
        if interval == 10000 and size == 8640:
            log.info("Displaying last 8640 readings (one day)")

            self.hist[0] = self.hist[0][-8640:]
            self.hist[1] = self.hist[1][-8640:]
            self.hist[2] = self.hist[2][-8640:]
            self.hist[3] = self.hist[3][-8640:]
            self.hist[4] = self.hist[4][-8640:]
            self.hist[5] = self.hist[5][-8640:]

        # Assumes that if you specify 144000 60 second readings, you want 100
        # days of data
        if interval == 60000 and size == 144000:
            log.info("Displaying last 144000 readings (100 days)")
            self.hist[0] = self.hist[0][0::6]
            self.hist[1] = self.hist[1][0::6]
            self.hist[2] = self.hist[2][0::6]
            self.hist[3] = self.hist[3][0::6]
            self.hist[4] = self.hist[4][0::6]
            self.hist[5] = self.hist[5][0::6]


        self.render_graph()

    def hist_assign(self, row, name="Average"):
        """ Assign the various min, max, or average values
        """
        self.hist[0] = numpy.append(self.hist[0],
                                    float(row["CCD %s" % name]))

        self.hist[1] = numpy.append(self.hist[1],
                                    float(row["Laser Temperature %s" % name]))

        self.hist[2] = numpy.append(self.hist[2],
                                    float(row["Laser Power %s" % name]))

        if name == "Min":
            # CSV file header has lower case thermistor for min
            self.hist[3] = numpy.append(self.hist[3],
                                        float(row["Yellow thermistor min"]))

            self.hist[4] = numpy.append(self.hist[4],
                                        float(row["Blue thermistor min"]))

        else:
            self.hist[3] = numpy.append(self.hist[3],
                                        float(row["Yellow Thermistor %s" % name]))

            self.hist[4] = numpy.append(self.hist[4],
                                        float(row["Blue Thermistor %s" % name]))

        self.hist[5] = numpy.append(self.hist[5],
                                    float(row["Amps %s" % name]))

    def bind_custom_actions(self):
        """ Toggle the display of graph curve items when the action buttons are
        checked in the action bar.
        """
        self.form.ui.actionCCD_Temp.triggered[bool].connect(self.ccd_temp_action)
        self.form.ui.actionLaser_Temp.triggered[bool].connect(self.laser_temp_action)
        self.form.ui.actionLaser_Power.triggered[bool].connect(self.laser_power_action)
        self.form.ui.actionYellow_Therm.triggered[bool].connect(self.yellow_therm_action)
        self.form.ui.actionBlue_Therm.triggered[bool].connect(self.blue_therm_action)
        self.form.ui.actionAmps.triggered[bool].connect(self.amps_action)

    def laser_power_action(self, action):
        self.toggle_curve(index=0, action=action)

    def laser_temp_action(self, action):
        self.toggle_curve(index=1, action=action)

    def ccd_temp_action(self, action):
        self.toggle_curve(index=2, action=action)

    def yellow_therm_action(self, action):
        self.toggle_curve(index=3, action=action)

    def blue_therm_action(self, action):
        self.toggle_curve(index=4, action=action)

    def amps_action(self, action):
        self.toggle_curve(index=5, action=action)

    def toggle_curve(self, index, action):
        log.debug("Action %s, index: %s", action, index)
        if action == False:
            self.form.plots[index][1].hide()
        else:
            self.form.plots[index][1].show()

    def create_data_sources(self):
        """ Pre-populate data structures for use in storing and rolling
        windows of data.
        """
        data_source = [
                        {"name":"CCD Temperature"},
                        {"name":"Laser Temperature"},
                        {"name":"Laser Power"},
                        {"name":"Yellow Therm"},
                        {"name":"Blue Therm"},
                        {"name":"Amperes"},
                      ]

        # Histories of data
        self.hist = []

        for item in data_source:
            self.hist.append(numpy.empty(0))

        # Local histories of data points to average
        self.local = []
        for item in data_source:
            self.local.append(numpy.empty(0))


    def event_loop(self):
        """ Process queue events, interface events, then update views.
        """

        result = self.device.read()
        # ltemp, power
        if result is not None:
            #print "raw result: ", result

            self.read_frames += 1
            self.reported_frames = result[0]
            #log.debug("Frame: %s", result)

            hist_count = 0
            for sensor_read in result[1]:
                #log.info("Append to local %s, value %s", hist_count, sensor_read)
                temp_array = self.local[hist_count]
                temp_array = numpy.append(temp_array, sensor_read)
                self.local[hist_count] = temp_array

                hist_count += 1

            # When in realtime mode, reassign the locally collected data to the
            # history
            if self.update_time_interval == 0:
                self.update_realtime()

        # Always restart this data collection procedure. A separate time for the
        # historical append copies the average of self.local to the appropriate
        # history when loaded from file
        self.main_timer.start(0)

    def update_realtime(self):
        """ Copy the most recently collected local datapoint to the history,
        display on screen.  """

        hist_count = 0
        for item in self.hist:
            local_val = self.local[hist_count][-1]

            temp_array = self.hist[hist_count]
            if len(temp_array) >= self.history_size:
                temp_array = numpy.roll(temp_array, -1)
                temp_array[-1] = local_val

            else:
                temp_array = numpy.append(temp_array, local_val)

            self.hist[hist_count] = temp_array
            hist_count += 1

        self.render_graph()
        self.update_performance_metrics()


    def update_history(self):
        """ Every update time interval, collate the local averages read off the
        network on to the full device histories.
        """

        #log.info("update history")
        hist_count = 0
        for item in self.hist:
            local_avg = numpy.average(self.local[hist_count])

            temp_array = self.hist[hist_count]
            if len(temp_array) >= self.history_size:
                temp_array = numpy.roll(temp_array, -1)
                temp_array[-1] = local_avg

            else:
                temp_array = numpy.append(temp_array, local_avg)
            self.hist[hist_count] = temp_array

            self.local[hist_count] = numpy.empty(0)

            hist_count += 1

        self.render_graph()
        self.update_performance_metrics()
        self.update_history_timer.start(self.update_time_interval)


    def render_graph(self):
        """ Update the graph data, indicate minimum and maximum values.
        """
        if not self.live_updates:
            return

        # display order is different then recording order
        # display zero is collection 2 (laser power)
        curve = self.form.plots[0][1]
        curve.setData(self.hist[2])

        # Display one is collection 1 (laser temperature)
        curve = self.form.plots[1][1]
        curve.setData(self.hist[1])

        # Display two is collection 0 (ccd temperature)
        curve = self.form.plots[2][1]
        curve.setData(self.hist[0])

        # Display three is collection three (yellow therm)
        curve = self.form.plots[3][1]
        curve.setData(self.hist[3])

        # Display four is collection four (blue therm)
        curve = self.form.plots[4][1]
        curve.setData(self.hist[4])

        # Display five is collection five (amps)
        curve = self.form.plots[5][1]
        curve.setData(self.hist[5])


        current_array = self.hist[2] # collection 2 is laser power
        if len(current_array) > 0:
            min_text = "%0.3f mw" % numpy.min(current_array)
            max_text = "%0.3f mw" % numpy.max(current_array)
            self.form.ui.labelMinimum.setText(min_text)
            self.form.ui.labelMaximum.setText(max_text)

        self.total_rend += 1

