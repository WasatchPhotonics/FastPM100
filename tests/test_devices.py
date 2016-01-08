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


    @pytest.fixture(scope="function")
    def sub_device(self, request):
        """ Setup the logger, the device inside the sub process, ensure the
        logging is closed correctly on exit.
        """
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()
        device = devices.SubProcessSimulatedPM100(main_logger.log_queue)

        def close_device():
            device.close()
            main_logger.close()
            applog.explicit_log_close()
        request.addfinalizer(close_device)

        return device

    def test_subprocess_data_collected_and_logged(self, sub_device, caplog):

        # Ensure at least one entry is available on the queue
        result = sub_device.read()
        while result is None:
            result = sub_device.read()

        assert result[0] == 1
        assert result[1] >= 123

        time.sleep(0.5) # Give subprocess log entries time to propagate to file
        log_text = applog.get_text_from_log()

        assert "SimulatedPM100 setup" in log_text
        assert "SimulatedPM100 setup" not in caplog.text()
        #assert "Collected data in continuous" in log_text
        #assert "Collected data in continuous" not in caplog.text()


    def test_subprocess_good_reads_matches_metric(self, sub_device, caplog):

        # Block in the parent process, allow the sub process to add entries to
        # the queue
        time.sleep(1.0)

        good_reads = 1
        result = sub_device.read()

        # There should now be a huge list of entries, read them all off, and
        # make sure the total count read off matches the total count of reads
        # reported by the sub process
        last_result = result
        while result is not None:
            result = sub_device.read()
            if result is not None:
                last_result = result
                good_reads += 1

        full_size = last_result[0]
        assert good_reads == full_size
        assert good_reads >= 100

