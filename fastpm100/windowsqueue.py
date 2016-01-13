""" Windows-focused Single queue sub process control and response.
"""

import time
import Queue
import numpy
import logging
import platform
import multiprocessing

from . import applog, devices

log = logging.getLogger(__name__)

class SubProcess(object):
    """ Wrap a specified device in a separate process.
    """

    timeout = 0.1

    def __init__(self, log_queue=None):
        self.results = multiprocessing.Queue(maxsize=1)
        self.control = multiprocessing.Queue(maxsize=1)

        args = (log_queue, self.results, self.control)
        self.proc = multiprocessing.Process(target=self.run, args=args)

        self.proc.start()


    def close(self):
        log.debug("Put poison pill on control queue")
        self.control.put(None, block=True, timeout=1.0)

        self.proc.join(0.1)
        self.proc.terminate()
        log.debug("Post proc terminate")


    def run(self, log_queue, results, control):
        applog.process_log_configure(log_queue)

        self.device = devices.SimulatedPM100()

        self.queue_empty_count = 0

        while True:
            res_control = self.get_or_none(self.control)
            if res_control is None:
                log.critical("None poison pill, or empty queue, break")
                log.critical("Queue empty count: %s",
                             self.queue_empty_count)
                break

        log.debug("Outside main run, exiting")

    def read(self):
        log.debug("Get a read")
        return None

    def get_or_none(self, queue):
        if queue.empty():
            self.queue_empty_count += 1
            #log.debug("queue is empty, exit with None")
            return False

        result = None
        try:
            result = queue.get(block=True, timeout=self.timeout)
        except Queue.Empty:
            log.debug("Get or none queue empty")
        except Exception as exc:
            log.critical("Other exception: %s", exc)

        return result

"""
qt app
    every qt event timeout, read from data queue
    if data queue is empty, do nothing
    if data queue is full, read off

sub process
    as fast as possible, read from data source, put on queue
    if queue is full, do nothing
    if queue is empty, put on queue

    if control queue is full, read off, if None, quit

control queue

That's a different mode and it may address the issues if the problem is
that on windows it's slow to handle the exceptions. Now you're just
checking the queue status as fast as possible, instead of attempting
operations that will create an exception.
"""
