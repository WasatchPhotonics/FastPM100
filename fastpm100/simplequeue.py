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

        while True:

            if control.full():
                self.print_exit_stats()
                break

            self.read_count += 1
            msg = (self.read_count, 123.0)

            if results.empty():
                results.put(msg)

            time.sleep(0.01)

        log.debug("End of run while")

    def print_exit_stats(self):
        log.debug("Total reads: %s", self.read_count)

    def close(self):
        log.debug("%s close", __name__)

        log.debug("Add none to control poison pill")
        self.control.put(None, block=True, timeout=1.0)

        self.proc.join(1.1)
        self.proc.terminate()
        log.debug("Close completion post terminate")

    def read(self):
        log.debug("%s read", __name__)
        get_result = self.results.get(block=True, timeout=1.0)
        return get_result

