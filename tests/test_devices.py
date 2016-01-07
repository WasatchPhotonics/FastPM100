""" Provide a set of tests cases to demonstrate a basic device that meets
wasatch needs. This includes simple blocking and long polling separate process
devices.
"""

import time
import pytest

from PySide import QtCore, QtTest

from fastpm100 import devices
from fastpm100 import applog

class TestBasicDevice:

    def test_direct_logging_is_available(self, caplog):
        device = devices.SimulateSpectra()
        assert "SimulateSpectra setup" in caplog.text()
        applog.explicit_log_close()

    def test_direct_device_is_available(self, caplog):
        device = devices.SimulateSpectra()
        result = device.read()
        assert len(result) == 1024
        applog.explicit_log_close()

    def test_subprocess_device_logging_is_unavailable(self, caplog):
        """ Shows the expected interactions between py.test, the caplog fixture,
        and logging from subprocesses. Specifically that pytest does not see the
        log statements printed from subprocess, you have to read them back from
        the file.
        """
        device = devices.LongPollingSimulateSpectra()
        device.close()
        assert "SimulateSpectra setup" not in caplog.text()
        applog.explicit_log_close()

    def test_subprocess_device_logging_in_file(self, caplog):
        """ Define the application wide queue handler for the logging, assign it
        to the device process. This test is about demonstrating actual usage in
        order to process the results in py.test.
        One of the confusing aspects here may be that in a bare bones
        application example, the log prints to the console still appear, on
        windows and linux. pytest does not see them however. Slurp them back in
        from the log file, which seems to work in executable, bare bones
        application, and pytest mode.
        """
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()

        device = devices.LongPollingSimulateSpectra(main_logger.log_queue)

        """ NOTE: these sleeps are critical on windows. They do not seem to
        matter on linux though. They have to be in the order listed below or the
        pytest run will hang on cleanup. That is, all the tests will be run,
        assertions processed, and it just hangs at the end of the run.
        """
        time.sleep(1.0) # make sure the process has enough time to emit
        device.close()

        main_logger.close()
        time.sleep(1.0) # required to let file creation happen

        log_text = applog.get_text_from_log()

        assert "SimulateSpectra setup" in log_text
        assert "SimulateSpectra setup" not in caplog.text()
        applog.explicit_log_close()

    def test_subprocess_data_collect_is_logged_in_file(self, caplog):
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()

        device = devices.LongPollingSimulateSpectra(main_logger.log_queue)

        result = device.read()
        while result is None:
            time.sleep(0.2)
            print "Read: %s" % result
            result = device.read()

        assert len(result) == 1024

        device.close()
        time.sleep(1.0) # make sure the process has enough time to emit

        main_logger.close()
        time.sleep(1.0) # required to let file creation happen

        log_text = applog.get_text_from_log()

        assert "Collected data in continuous" in log_text
        assert "Collected data in continuous" not in caplog.text()
        applog.explicit_log_close()
