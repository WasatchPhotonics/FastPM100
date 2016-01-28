""" logging from multiple processes to a single handler is critical to wasatch
application goals. These tests ensure that the various components of the
application all log to same location on disk.

As of 2015-12-30 10:39, it is unknown how to work with py.test and the
capturelog fixture to read the log prints to stdout/stderr streams. The
workaround is to store all of the log events to disk, and re-read the file at
test completion.

"""

import os
import time
import logging
import multiprocessing

from fastpm100 import applog

@pytest.mark.skipif(not pytest.config.getoption("--wrapper"),
                    reason="need --wrapper option to run")
class TestLogFile():
    def test_log_file_is_created(self):
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()
        main_logger.close()

        time.sleep(3.5) # required to let file creation happen

        assert applog.log_file_created() == True
        applog.explicit_log_close()


    def test_log_file_has_entries(self):
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()
        main_logger.close()

        time.sleep(3.5) # required to let file creation happen

        log_text = applog.get_text_from_log()

        assert "Top level log configuration" in log_text
        applog.explicit_log_close()


    def test_log_capture_fixture_can_read_top_level_log(self, caplog):
        main_logger = applog.MainLogger()
        main_logger.close()

        assert "Top level log configuration" in caplog.text()
        applog.explicit_log_close()


    def test_log_capture_fixture_does_not_see_sub_process_entries(self, caplog):
        """ This test is about documenting the expected behavior. It took days
        of effort to determine that the logging is behaving as expected, but the
        pytest capture fixtures does not seem to be able to record those values.
        """
        main_logger = applog.MainLogger()

        log_queue = main_logger.log_queue
        sub_proc = multiprocessing.Process(target=self.worker_process,
                                           args=(log_queue,))
        sub_proc.start()

        time.sleep(6.0) # make sure the process has enough time to emit

        main_logger.close()

        time.sleep(3.5) # required to let file creation happen

        log_text = caplog.text()

        assert "Top level log configuration" in log_text
        assert "Sub process setup configuration" not in log_text
        assert "Sub process debug log info" not in log_text
        applog.explicit_log_close()

    def test_log_file_has_sub_process_entries(self):
        """ This test documents the alternative: slurp the log results back in
        from the log file and then do the text matches.
        """
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()

        log_queue = main_logger.log_queue
        sub_proc = multiprocessing.Process(target=self.worker_process,
                                           args=(log_queue,))
        sub_proc.start()

        time.sleep(6.0) # make sure the process has enough time to emit

        main_logger.close()

        time.sleep(3.5) # required to let file creation happen

        log_text = applog.get_text_from_log()

        assert "Top level log configuration" in log_text
        assert "Sub process setup configuration" in log_text
        assert "Sub process debug log info" in log_text
        applog.explicit_log_close()


    def worker_process(self, log_queue):
        """ Simple multi-processing target that uses the helper log
        configuration in applog, and logs the current process name and an
        expected string.
        """

        applog.process_log_configure(log_queue)

        # The root logger has now been created for this process, along with the
        # queue handler. Get a reference to the root_log and write a debug log
        # entry. In a real application the module level log =
        # logging.getLogger(__name__) still will be called, but then the log
        # module level variable will be overwritten witht the root logger
        # created in the applog.process_log_configure call above.
        root_log = logging.getLogger()

        proc_name = multiprocessing.current_process().name

        root_log.debug("%s Sub process debug log info", proc_name)

