""" Use queue empty and full checks instead of exception catching for clearer
and hopefully faster communications on windows and linux.
"""

import time
import Queue

from multiprocessing import Queue as MPQueue
from multiprocessing import Process

from fastpm100 import applog, devices

import logging
log = logging.getLogger(__name__)

class SubProcess(object):
    def __init__(self, log_queue, delay_time=None):
        log.debug("%s startup", __name__)

        self.results = MPQueue(maxsize=1)
        self.control = MPQueue(maxsize=1)

        args = (log_queue, delay_time,
                self.results, self.control)
        self.proc = Process(target=self.run, args=args)
        self.proc.start()

    def run(self, log_queue, delay_time, results, control):

        applog.process_log_configure(log_queue)
        self.read_count = 0

        self.device = devices.SimulatedPM100()

        log.debug("Start of while loop with delay [%s]", delay_time)
        while True:

            if control.full():
                log.debug("Control queue full, exit poison pill")
                self.print_exit_stats()
                break

            self.read_count += 1
            msg = (self.read_count, self.device.read())

            if results.empty():
                try:
                    results.put(msg, block=False)

                # Silent failures on exit if you don't catch this exception
                except Queue.Full:
                    pass

            if delay_time is not None:
                time.sleep(delay_time)

        log.debug("End of run while")

    def print_exit_stats(self):
        log.debug("Total reads: %s", self.read_count)

    def close(self):
        """ Add the poison pill to the control queue. Join, then terminate the
        threads on timeout.
        """
        log.debug("Add none to control poison pill")
        try:
            self.control.put(None, block=True, timeout=1.0)
        except Queue.Full:
            log.critical("Can't add poison pill")

        self.proc.join(timeout=0.1)
        self.proc.terminate()

        log.debug("Close completion post terminate")

    def read(self):
        """ Return None from the queue if it's ever empty for a second.
        Otherwise return the actual value from the queue.
        """
        get_result = None
        try:
            get_result = self.results.get(block=False)
        except Queue.Empty:
            log.critical("Results queue is empty")

        return get_result

