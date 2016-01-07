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
        assert len(result) == 1
        applog.explicit_log_close()

    def test_direct_device_randomized(self):
        device = devices.SimulatedPM100()
        result = device.read()
        assert len(result) == 1
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

        assert len(result) == 1

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


