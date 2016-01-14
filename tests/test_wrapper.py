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
        """ Setup the logger, the device inside the sub process, ensure the
        logging is closed correctly on exit.
        """
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()
        sub_proc = wrapper.SubProcess(main_logger.log_queue)

        def close_sub_proc():
            sub_proc.close()
            main_logger.close()
            applog.explicit_log_close()
        request.addfinalizer(close_sub_proc)

        start_wait = 1.0
        log.debug("Wait %s for sub process to start", start_wait)
        time.sleep(start_wait)
        return sub_proc

    def test_setup_read_and_exit(self, wrapper):

        result = wrapper.read()
        log.debug("Test read back %s", result)
        assert result[0] == 1
        assert result[1] >= 123.0

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

    def test_controller_rate_and_data_rate_independent(self, wrapper):
        result = self.read_while_none(wrapper)
        time.sleep(1.0)

        result = self.read_while_none(wrapper)
        log.debug("second read: %s", result)
        dfps = result[0]
        # Controller rate here is 2 FPS
        # data rate should be much higher
        assert dfps >= 1000


