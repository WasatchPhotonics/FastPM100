""" Testing tests for getting log prints in multiprocessing objects
with py.test and pyside, etc.
"""

import sys
import time

import logging
log = logging.getLogger()
strm = logging.StreamHandler(sys.stderr)
frmt = logging.Formatter("%(name)s - %(levelname)s %(message)s")
strm.setFormatter(frmt)
log.addHandler(strm)
log.setLevel(logging.DEBUG)

import multiprocessing
multiprocessing.log_to_stderr(logging.DEBUG)


class TestProcessLogs:
    def test_object_has_log_debug(self):
        from fastpm100 import devices
        mp_device = devices.QueueMPDevice()
        mp_device.create()

        sleep_dur = 1
        count = 0
        while(1):
            log.debug("Sleep: %s", sleep_dur)
            time.sleep(sleep_dur)
            count += 1
            if count > 3:
                break

        mp_device.close()


    #def test_object_called_linked_in_pyside_has_log_prints(self):

