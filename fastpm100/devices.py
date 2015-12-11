""" Classes for device control testing around pm100 and multiprocessing
"""

import sys
import time
import Queue
import platform
import multiprocessing

import logging
log = logging.getLogger(__name__)
#multiprocessing.log_to_stderr(logging.DEBUG)


class QueueMPDevice(object):
    """ Use the poison pill pattern to exit the worker thread.
    """
    def __init__(self):
        log.debug("Init of %s", self.__class__.__name__)
        super(QueueMPDevice, self).__init__()

        self.queue = multiprocessing.Queue()
        mpp = multiprocessing.Process
        self.process = mpp(target=self.worker, args=(self.queue,))
        self.process.daemon = True

    def create_new_log_on_windows(self):
        """ If operating on MS windows in a multiprocessing context, the
        log prints to stderr will not appear. Create a new logger with a
        formatter to stderr if operating on windows only. Do not do this
        on Linux as it will print dual log messages.
        """
        if "Windows" in platform.platform():
            self.my_log = logging.getLogger()
            strm = logging.StreamHandler(sys.stderr)
            frmt = logging.Formatter("%(name)s - %(levelname)s %(message)s")
            strm.setFormatter(frmt)
            self.my_log.addHandler(strm)
            self.my_log.setLevel(logging.DEBUG)
            self.my_log.debug("Dual windows log setup")
            return self.my_log

        return log

    def worker(self, queue):
        log = self.create_new_log_on_windows()

        while(True):
            #self.my_log.debug("In while loop")
            #print("print in while loop")
            #sys.stdout.flush()
            # Remember this will hang on python 2.7 on windows - the
            # queue empty exception, that is
            result = None
            try:
                result = queue.get_nowait()
            except Queue.Empty:
                #log.debug("Queue is empty")
                pass

            if result == "DISCONNECT":
                log.debug("Disonnect received, exiting loop")
                break

            current = multiprocessing.current_process()
            self.my_log.debug("Worker process: %s", current.pid)
            time.sleep(0.3)

    def create(self):
        log.debug("Start the multiprocessing object")
        self.process.start()
        log.debug("post Start the multiprocessing object")

    def close(self):
        log.debug("Join the multiprocessing object")
        self.queue.put("DISCONNECT")
        self.process.join()
