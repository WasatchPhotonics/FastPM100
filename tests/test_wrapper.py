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

        return sub_proc

    def test_setup_read_and_exit(self, wrapper):

        # post creation sleep
        time.sleep(1.0)

        result = wrapper.read()
        log.debug("Test read back %s", result)
        assert result[0] == 1
        assert result[1] >= 123.0

        result = wrapper.read()
        log.debug("second Test read back %s", result)
