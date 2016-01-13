""" Use queue empty and full checks instead of exception catching for clearer
and hopefully faster communications on windows and linux.
"""

import time

from multiprocessing import Queue as MPQueue
from multiprocessing import Process

from fastpm100 import applog, devices

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

        self.device = devices.SimulatedPM100()

        log.debug("Start of while loop")
        while True:

            if control.full():
                log.debug("Control queue full, exit poison pill")
                self.print_exit_stats()
                break

            self.read_count += 1
            msg = (self.read_count, self.device.read())

            if results.empty():
                results.put(msg)

            # This is required to have py.test see the exit control
            time.sleep(0.01)

        log.debug("End of run while")

    def print_exit_stats(self):
        log.debug("Total reads: %s", self.read_count)

    def close(self):
        log.debug("Add none to control poison pill")
        self.control.put(None, block=True, timeout=1.0)

        self.proc.join(timeout=0.1)
        self.proc.terminate()

        # Docs say join after terminate as well
        self.proc.join(timeout=0.1)

        log.debug("Close completion post terminate")

    def read(self):
        log.debug("%s read", __name__)
        get_result = self.results.get(block=True, timeout=1.0)
        return get_result

