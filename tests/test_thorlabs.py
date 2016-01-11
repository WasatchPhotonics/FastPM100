""" Provide a set of tests cases to demonstrate basic communication with
thorlabs pm100 usb.
"""

import time
import pytest

from PySide import QtCore, QtTest

from fastpm100 import applog

class TestThorlabsPM100:

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

