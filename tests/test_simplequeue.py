""" Verify the functionality of "simple" queue full and empty checks.
"""

import time
import pytest

from fastpm100 import simplequeue, applog

import logging
log = logging.getLogger(__name__)

#@pytest.mark.skipif(not pytest.config.getoption("--hardware"),
                    #reason="need --hardware option to run")
class TestSimpleQueue:

    @pytest.fixture(scope="function")
    def sub_device(self, request):
        """ Setup the logger, the device inside the sub process, ensure the
        logging is closed correctly on exit.
        """
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()
        device = simplequeue.SubProcess(main_logger.log_queue)

        def close_device():
            device.close()
            main_logger.close()
            applog.explicit_log_close()
        request.addfinalizer(close_device)

        return device

    def test_setup_read_and_exit(self, sub_device):

        # post creation sleep
        time.sleep(5.0)

        result = sub_device.read()
        log.debug("Test read back %s", result)
        assert result[0] == 0
        assert result[1] >= 123.0

        log.debug("End test area, start cleanup")

