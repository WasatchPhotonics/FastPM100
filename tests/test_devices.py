""" Provide a set of tests cases to demonstrate a basic device that meets
wasatch needs. This includes simple blocking and long polling separate process
devices.
"""

import time
import pytest

from fastpm100 import devices, applog

@pytest.mark.skipif(pytest.config.getoption("--appveyor"),
                    reason="need --appveyor option to disable tests")
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

    def test_sleep_factor_slows_down_reads(self):
        device = devices.SimulatedPM100(sleep_factor=1.0)
        result = device.read()

        assert result != 0
        assert result != None

        start_time = time.time()
        new_result = device.read()
        cease_time = time.time()

        time_diff = cease_time - start_time
        assert time_diff >= 1.0

        assert result != new_result
        applog.explicit_log_close()


@pytest.mark.skipif(pytest.config.getoption("--appveyor"),
                    reason="need --appveyor option to disable tests"
                    "with physical hardware requirement")
class TestSlapChopDevice:

    def test_slapchop_direct_logging_is_available(self, caplog):
        device = devices.SlapChopDevice()
        assert "SlapChopDevice setup" in caplog.text()
        applog.explicit_log_close()

    def test_slapchop_direct_device_is_available(self, caplog):
        device = devices.SlapChopDevice()
        result = device.read()

        assert result != 0
        assert result != None

        applog.explicit_log_close()

    def test_slapchop_values_change(self, caplog):
        device = devices.SlapChopDevice()
        first_result = device.read()
        second_result = device.read()

        assert first_result != second_result

        applog.explicit_log_close()
