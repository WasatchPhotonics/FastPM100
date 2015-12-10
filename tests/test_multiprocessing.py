""" Working tests for verifying open, close, and logging in various
processing objects.
"""

import multiprocessing

import sys
import logging
log = logging.getLogger()
strm = logging.StreamHandler(sys.stderr)
frmt = logging.Formatter("%(name)s - %(levelname)s %(message)s")
strm.setFormatter(frmt)
log.addHandler(strm)
log.setLevel(logging.DEBUG)


def worker():
    #print "Doing some work"
    #sys.stdout.flush()
    log.debug("Doing some log work")


class TestProcessLogs:
    def test_print_log_at_debug(self):

        multiprocessing.log_to_stderr(logging.DEBUG)
        mp_device = multiprocessing.Process(target=worker)
        mp_device.start()
        mp_device.join()


        # What is that log output tracking from linegrab? or was it some
        # other project?
        assert True == False
