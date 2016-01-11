""" Provide a set of tests cases to demonstrate basic communication with
thorlabs pm100 usb.
"""

import time
import pytest

from PySide import QtCore, QtTest

from fastpm100 import applog, devices

class TestThorlabsPM100:

    @pytest.mark.xfail
    def test_direct_logging_is_available(self, caplog):
        device = devices.ThorlabsMeter()
        assert "ThorlabsMeter setup" in caplog.text()
        applog.explicit_log_close()

    @pytest.mark.xfail
    def test_direct_device_is_available(self, caplog):
        device = devices.ThorlabsMeter()
        result = device.read()

        assert result != 0
        assert result != None
        assert result >= 0.0

        applog.explicit_log_close()

    @pytest.mark.xfail
    def test_direct_device_looks_real(self):
        device = devices.ThorlabsMeter()
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
        device = devices.SubProcessThorlabsMeter(main_logger.log_queue)

        def close_device():
            device.close()
            main_logger.close()
            applog.explicit_log_close()
        request.addfinalizer(close_device)

        return device

    @pytest.mark.xfail
    def test_subprocess_data_collected_and_logged(self, sub_device, caplog):

        # Ensure at least one entry is available on the queue
        result = sub_device.read()
        while result is None:
            result = sub_device.read()

        assert result[0] == 1
        assert result[1] > 0.0

        time.sleep(0.5) # Give subprocess log entries time to propagate to file
        log_text = applog.get_text_from_log()

        assert "ThorlabsMeter setup" in log_text
        assert "ThorlabsMeter setup" not in caplog.text()

    @pytest.mark.xfail
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
        assert good_reads >= 10

