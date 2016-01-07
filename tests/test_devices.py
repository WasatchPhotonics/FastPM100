""" Provide a set of tests cases to demonstrate a basic device that meets
wasatch needs. This includes simple blocking and long polling separate process
devices.
"""

import time
import pytest

from PySide import QtCore, QtTest

from fastpm100 import devices
from fastpm100 import applog

class TestSimulatedPM100Device:

    def test_direct_logging_is_available(self, caplog):
        device = devices.SimulatedPM100()
        assert "SimulatedPM100 setup" in caplog.text()
        applog.explicit_log_close()

    def test_direct_device_is_available(self, caplog):
        device = devices.SimulatedPM100()
        result = device.read()

        assert result != 0
        assert result != None

        applog.explicit_log_close()

    def test_direct_device_randomized(self):
        device = devices.SimulatedPM100()
        result = device.read()

        assert result != 0
        assert result != None

        new_result = device.read()
        assert result != new_result
        applog.explicit_log_close()

    def test_subprocess_data_collected_and_logged(self, caplog):
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()

        device = devices.LongPollingSimulatedPM100(main_logger.log_queue)

        result = device.read()
        while result is None:
            time.sleep(0.2)
            print "Read: %s" % result
            result = device.read()

        assert result != 0
        assert result != None

        device.close()
        time.sleep(1.0) # make sure the process has enough time to emit

        main_logger.close()
        time.sleep(1.0) # required to let file creation happen

        log_text = applog.get_text_from_log()

        assert "SimulatedPM100 setup" in log_text
        assert "SimulatedPM100 setup" not in caplog.text()
        assert "Collected data in continuous" in log_text
        assert "Collected data in continuous" not in caplog.text()
        applog.explicit_log_close()

    @pytest.fixture(scope="function")
    def sub_device(self, request):
        """ Setup the logger, the device inside the sub process, ensure the
        logging is closed correctly on exit.
        """
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()
        device = devices.LongPollingSimulatedPM100(main_logger.log_queue)

        def close_device():
            device.close()
            main_logger.close()
            applog.explicit_log_close()
        request.addfinalizer(close_device)

        return device

    def test_default_speed_that_matches_explicit_acquire(self, sub_device, caplog):
        """ In the default configuration, every call to read() sends an acquire,
        and gets the next entry off the queue at the next read. Ensure that the
        default behavior returns 10 reads in 1 second with the appropriate time
        interval in the parent process.  """

        start_time = time.time()
        cease_time = time.time()
        time_diffe = cease_time - start_time

        good_reads = 0
        while time_diffe <= 1.1:
            result = sub_device.read()
            time.sleep(0.05) # 100ms total, first to read, then get the next
            if result is not None:
                good_reads += 1

            cease_time = time.time()
            time_diffe = cease_time - start_time

        print "Received %s reads in %s seconds" % (good_reads, time_diffe)
        assert good_reads >= 8
        assert good_reads <= 11


    @pytest.fixture(scope="function")
    def fast_device(self, request):
        """ Sub process device that reads repeatedly, without waiting for the
        acquire command, as in sub_device.
        """
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()
        device = devices.LongPollingSimulatedPM100(main_logger.log_queue,
                                                   auto_acquire=True)
        #device = devices.FastSimulatedPM100(main_logger.log_queue)

        def close_device():
            device.close()
            main_logger.close()
            applog.explicit_log_close()
        request.addfinalizer(close_device)

        return device

    def test_auto_acquire_speed_is_faster(self, fast_device, caplog):
        """ With the auto_acquire flag on, verify that the device reports
        significantly higher acquisition rates.
        """
        start_time = time.time()
        cease_time = time.time()
        time_diffe = cease_time - start_time

        good_reads = 0
        while time_diffe <= 1.1:
            # Sub-process in auto-acquire is still running despite this blocking
            # sleep
            time.sleep(0.05)
            result = fast_device.read()
            while result is not None:
                result = fast_device.read()
                good_reads += 1

            cease_time = time.time()
            time_diffe = cease_time - start_time

        print "Received %s reads in %s seconds" % (good_reads, time_diffe)
        assert good_reads >= 1000
