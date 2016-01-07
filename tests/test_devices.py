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

    def test_reports_speed_that_matches_explicit_acquire(self, sub_device, caplog):
        """ In the default configuration, every call to read() sends an acquire,
        and gets the next entry off the queue at the next read. Ensure that the
        default behavior returns 10 reads in 1 second with the appropriate time
        interval in the parent process.  """

        result = sub_device.read()
        while result is None:
            time.sleep(0.2)
            print "Read: %s" % result
            result = sub_device.read()

        assert result != 0
        assert result != None

        log_text = applog.get_text_from_log()

        assert "SimulatedPM100 setup" in log_text
        assert "SimulatedPM100 setup" not in caplog.text()
        assert "Collected data in continuous" in log_text
        assert "Collected data in continuous" not in caplog.text()

