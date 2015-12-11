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

        # Check for the sys attribute here, as windows removes it from
        # subsequent processing imports.
        self.in_test = None
        if hasattr(sys, "_called_from_test"):
            log.debug("Pytest call, will re-create log for process")
            self.in_test = True

        self.queue = multiprocessing.Queue()
        args = (self.queue, self.in_test)

        mpp = multiprocessing.Process
        self.process = mpp(target=self.worker, args=args)
        self.process.daemon = True

    def create_new_log_on_windows_with_pytest(self, in_test):
        """ If operating on MS windows in a multiprocessing context
        while using pytest, the log prints to stderr will not appear.
        Create a new logger with a formatter to stderr if operating on
        windows only, and only if called within pytest. This is a non
        issue on Linux, apparently because of the presence of fork().
        """

        if in_test is not None:
            if "Windows" in platform.platform():
                self.my_log = logging.getLogger()
                strm = logging.StreamHandler(sys.stderr)
                frmt = logging.Formatter("%(asctime)s %(name)s - %(levelname)s %(message)s")
                strm.setFormatter(frmt)
                self.my_log.addHandler(strm)
                self.my_log.setLevel(logging.DEBUG)
                self.my_log.debug("Dual windows log setup")
                return self.my_log

        return log

    def worker(self, queue, in_test):
        log = self.create_new_log_on_windows_with_pytest(in_test)

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
            log.debug("Worker process: %s", current.pid)
            time.sleep(0.3)

    def create(self):
        log.debug("Start the multiprocessing object")
        self.process.start()
        log.debug("post Start the multiprocessing object")

    def close(self):
        log.debug("Join the multiprocessing object")
        self.queue.put("DISCONNECT")
        self.process.join()
