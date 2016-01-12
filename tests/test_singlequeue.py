""" Poison pill control and single length queue for easier to grok performance
measurements.  """

import time
import pytest

from fastpm100 import singlequeue, applog

class TestSingleQueue:
    def test_queue_open_and_close(self):

        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()
        device = singlequeue.SubProcess(main_logger.log_queue)

        device.close()
        main_logger.close()
        applog.explicit_log_close()

    @pytest.fixture(scope="function")
    def device(self, request):
        """ Setup the sub process device in the single queue control section.
        Ensure the logging is closed correctly on exit.
        """

        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()
        device = singlequeue.SubProcess(main_logger.log_queue)

        def on_close():
            device.close()
            main_logger.close()
            applog.explicit_log_close()
        request.addfinalizer(on_close)

        return device

    def test_queue_returns_data(self, device):


        time.sleep(3.0)
        result = device.read()
        print " Last result ", result
        assert result[0] >= 100
        assert result[1] >= 123.0

