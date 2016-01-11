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

