""" Provide a set of tests cases to demonstrate basic communication with
thorlabs pm100 usb.
"""

import time
import pytest

from PySide import QtCore, QtTest

from fastpm100 import applog, devices

@pytest.mark.skipif(not pytest.config.getoption("--hardware"),
                    reason="need --hardware option to run")
class TestThorlabsPM100:

    def test_direct_logging_is_available(self, caplog):
        device = devices.ThorlabsMeter()
        assert "ThorlabsMeter setup" in caplog.text()
        applog.explicit_log_close()

    def test_direct_device_is_available(self, caplog):
        device = devices.ThorlabsMeter()
        result = device.read()

        assert result != 0
        assert result != None
        assert result >= 0.0

        applog.explicit_log_close()

    def test_direct_device_looks_real(self):
        device = devices.ThorlabsMeter()
        result = device.read()

        assert result != 0
        assert result != None

        new_result = device.read()
        assert result != new_result
        applog.explicit_log_close()


    def test_direct_device_read_is_fast(self, caplog):
        device = devices.ThorlabsMeter()
        start_time = time.time()

        max_reads = 1000
        for count in range(max_reads):
            result = device.read()
            #print "result %s, %s" % (count, result)

        cease_time = time.time()
        delta_time = cease_time - start_time

        reads_per_sec = max_reads / delta_time
        print "Time %s, max %s reads per %s" \
              % (delta_time, max_reads, reads_per_sec)

        # As of 2016-01-12 07:30 using USBTMC on fedora intel i5 and
        # using VISA on windows 7 i7 both return aroudn 330 reads per
        # second.
        assert delta_time <= 4.0
        assert delta_time >= 2.0
