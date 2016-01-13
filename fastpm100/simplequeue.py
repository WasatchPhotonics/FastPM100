""" Use queue empty and full checks instead of exception catching for clearer
and hopefully faster communications on windows and linux.
"""

import time

from multiprocessing import Queue as MPQueue
from multiprocessing import Process

from fastpm100 import applog

import logging
log = logging.getLogger(__name__)

class SubProcess(object):
    def __init__(self, log_queue):
        log.debug("%s startup", __name__)

        self.results = MPQueue(maxsize=1)
        self.control = MPQueue(maxsize=1)

        args = (log_queue, self.results, self.control)
        self.proc = Process(target=self.run, args=args)
        self.proc.start()

    def run(self, log_queue, results, control):

        applog.process_log_configure(log_queue)
        self.read_count = 0
        self.not_empty_count = 0
        self.control_full_count = 0
        self.control_void_count = 0

        while True:

            if control.full():
                self.control_full_count += 1
                log.debug("Data on control queue, exiting")
                self.print_exit_stats()
                break
            else:
                self.control_void_count += 1
                #log.debug("Control is full %s", self.control_full_count)

            if results.empty():
                log.debug("Put data on queue")
                results.put((self.read_count, 123.0))
            else:
                self.not_empty_count += 1
                #log.debug("non-empty %s", self.not_empty_count)

            # No sleep or this level on linux fedora core 22 intel i5 will not
            # print the control queue exit message and stats above when run in
            # pytest. Making it 0.000001 or  longer works fine
            #time.sleep(0.0000001)

            # This appears to be were windows and linux will converge their
            # performance. This reports 100 per second, if you go to 0.001 it
            # does 1k per second on linux and still 100 per second on windows
            time.sleep(0.010001)
            self.read_count += 1

        log.debug("End of run while")

    def print_exit_stats(self):
        log.debug("Total reads: %s", self.read_count)
        log.debug("Total non-empty result checks: %s", self.not_empty_count)
        log.debug("Total control queue is full %s", self.control_full_count)
        log.debug("Total control queue is void %s", self.control_void_count)


    def close(self):
        log.debug("%s close", __name__)

        log.debug("Add none to control poison pill")
        self.control.put(None, block=True, timeout=1.0)

        self.proc.join(0.1)
        self.proc.terminate()
        log.debug("Close completion post terminate")


    def read(self):
        log.debug("%s read", __name__)
        get_result = self.results.get(block=True, timeout=1.0)
        return get_result

