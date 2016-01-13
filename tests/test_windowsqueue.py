""" Windows -based. Poison pill control and single length queue for easier to grok performance
measurements.  """

import time
import pytest

from fastpm100 import windowsqueue, applog

import logging
log = logging.getLogger(__name__)

@pytest.mark.skipif(not pytest.config.getoption("--hardware"),
                    reason="need --hardware option to run")
class TestWindowsQueue:

    @pytest.fixture(scope="function")
    def device(self, request):
        """ Setup the sub process device in the single queue control section.
        Ensure the logging is closed correctly on exit.
        """

        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()
        device = windowsqueue.SubProcess(main_logger.log_queue)

        def on_close():
            device.close()
            main_logger.close()
            applog.explicit_log_close()
        request.addfinalizer(on_close)

        return device

    def test_queue_open_and_close(self, device):

        time.sleep(1.0)
        result = device.read()
        log.debug("One result is: %s", result[0])
        assert True == True

