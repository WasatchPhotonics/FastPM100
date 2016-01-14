""" Provide test cases that demonstrate a sub-process enabled wrapper around
device objects. This includes long druation reads and performance metrics.
"""

import time
import pytest

from fastpm100 import wrapper, applog, devices

import logging
log = logging.getLogger(__name__)

class TestWrapper:

    @pytest.fixture(scope="function")
    def wrapper(self, request):
        return self.build_sub_process(request, delay_time=None)

    @pytest.fixture(scope="function")
    def regulated_wrapper(self, request):
        return self.build_sub_process(request, delay_time=0.1)

    def build_sub_process(self, request, delay_time=None):
        """ Setup the logger, the device inside the sub process, ensure the
        logging is closed correctly on exit.
        """
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()
        sub_proc = wrapper.SubProcess(main_logger.log_queue,
                                      delay_time=delay_time)

        def close_sub_proc():
            sub_proc.close()
            main_logger.close()
            applog.explicit_log_close()
        request.addfinalizer(close_sub_proc)

        start_wait = 1.0
        log.debug("Wait %s for sub process to start", start_wait)
        time.sleep(start_wait)
        return sub_proc

    def read_while_none(self, wrap_interface, timeout=1.0):
        """ Read off the wrapper device until a result is available, or until a
        timeout has been reached. The wrapper will put an item back on the queue
        usually before a none can be read back from the results queue. This is a
        simple timeout on a read forever loop to try and make sure data is
        always returned.
        """
        start_time = time.time()
        inter_diff = time.time() - start_time

        while inter_diff <= timeout:
            result = wrap_interface.read()
            if result is not None:
                return result

            inter_diff = time.time() - start_time


        log.critical("Failure to read off wrapper in %s", timeout)
        raise NameError

    def test_setup_read_and_exit(self, wrapper):

        result = wrapper.read()
        log.debug("Test read back %s", result)
        assert result[0] == 1
        assert result[1] >= 123.0

    def test_subprocess_data_collected_and_logged(self, wrapper, caplog):

        # Ensure at least one entry is available on the queue
        result = self.read_while_none(wrapper)

        assert result[0] == 1
        assert result[1] >= 123

        time.sleep(0.5) # Give subprocess log entries time to propagate to file
        log_text = applog.get_text_from_log()

        assert "SimulatedPM100 setup" in log_text
        assert "SimulatedPM100 setup" not in caplog.text()


    def test_controller_rate_and_data_rate_independent(self, wrapper):
        result = self.read_while_none(wrapper)
        time.sleep(1.0)

        result = self.read_while_none(wrapper)
        log.debug("second read: %s", result)
        dfps = result[0]
        # Controller rate here is 2 FPS
        # data rate should be much higher
        assert dfps >= 1000

    def test_controller_rate_is_configurable(self, regulated_wrapper):
        """ Actual data rate should be regulated to near 10 fps. Add huge
        margins as CI servers may be under heavy load. You're not looking for
        precision in rate matching here. You're looking for 10k+ difference from
        the non regulated version.
        """

        result = self.read_while_none(regulated_wrapper)
        time.sleep(1.0)

        result = self.read_while_none(regulated_wrapper)
        log.debug("second read: %s", result)
        dfps = result[0]

        assert dfps >= 1
        assert dfps <= 15
