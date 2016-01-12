""" Poison pill control and single length queue for easier to grok performance
measurements.  """

import time
import pytest

from fastpm100 import singlequeue, applog

@pytest.mark.skipif(not pytest.config.getoption("--hardware"),
                    reason="need --hardware option to run")
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
        """ This test demonstrates that the queue clearer and reloader is
        running in the background. On z560 fedora, this shows >100k total reads
        over 3 seconds.
        """
        time.sleep(3.0)
        result = device.read()
        print " Last result is ", result
        assert result[0] >= 100
        assert result[1] >= 123.0

    #def test_queue_speed_is_independent(self, device):
        #""" Verify that
