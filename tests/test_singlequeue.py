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

    def test_queue_returns_data(self):


        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()
        device = singlequeue.SubProcess(main_logger.log_queue)

        time.sleep(1.0)
        result = device.read()
        assert result[0] == 1
        assert result[1] >= 123.0

        device.close()
        main_logger.close()
        applog.explicit_log_close()
