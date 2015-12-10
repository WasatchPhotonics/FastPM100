""" Classes for device control testing around pm100 and multiprocessing
"""

import time
import Queue
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

    def worker(self, queue):
        while(True):
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

    def close(self):
        log.debug("Join the multiprocessing object")
        self.queue.put("DISCONNECT")
        self.process.join()
