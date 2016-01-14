""" This is the bare-bones multiprocessing setup used for debugging the queue
exception silent exit issues.
"""
import time
import logging

import Queue
import multiprocessing
multiprocessing.log_to_stderr(logging.DEBUG)
log = multiprocessing.get_logger()

class SubProcess(object):
    def __init__(self):
        log.debug("%s startup", __name__)

        self.results = multiprocessing.Queue(maxsize=1)
        self.control = multiprocessing.Queue(maxsize=1)

        args = (self.results, self.control)
        self.proc = multiprocessing.Process(target=self.runit, args=args)
        self.proc.start()

    def runit(self, results, control):

        self.read_count = 0


        log.debug("Start of while loop")

        while self.read_count <= 10:

            self.read_count += 1
            msg = (self.read_count, 123.0)

            # This combination of queue empty check and sleep is usually ok,
            # which leads to confusion

            #if results.empty():
            #    results.put(msg, block=True, timeout=0.1)
            #    time.sleep(0.02)

            # This was the configuration that seems to work. If you take out the
            # try/except below, the program will terminate silently (only with
            # no sleep), and end of run while below will not print.
            if results.empty():
                try:
                    results.put(msg, block=False)
                except Queue.Full:
                    pass


        log.debug("End of run while")

    def close(self):
        self.proc.join(timeout=0.1)
        self.proc.terminate()

        # Docs say join after terminate as well
        self.proc.join(timeout=0.1)

        log.debug("Close completion post terminate")

    def read(self):
        log.debug("%s read", __name__)
        get_result = self.results.get(block=True, timeout=1.0)
        return get_result


if __name__ == "__main__":

    device = SubProcess()
    time.sleep(2.0)

    result = device.read()
    log.debug("Test read back %s", result)

    log.debug("End test area, start cleanup")

    device.close()

