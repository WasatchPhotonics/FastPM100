""" Simulated device components for demonstration program. Simple blocking calls
with simulated delays for simulated spectrometer readings. Long-polling
multiprocessing wrappers.
"""

import time
import Queue
import logging
import multiprocessing

from . import applog

log = logging.getLogger(__name__)

class SimulateSpectra(object):
    """ Provide a bare bones interface for reading simulated spectra from a
    simulated device.
    """
    def __init__(self):
        super(SimulateSpectra, self).__init__()
        log.debug("%s setup", self.__class__.__name__)

    def read(self):
        """ Return a test pattern of 0-1023 values across an 1024 length list.
        """
        return range(0, 1024)


class LongPollingSimulateSpectra(object):
    """ Wrap simulate spectra in a non-blocking interface run in a separate
    process.
    """
    def __init__(self, log_queue=None):
        self.response_queue = multiprocessing.Queue()
        self.command_queue = multiprocessing.Queue()

        self.acquire_sent = False # Wait for an acquire to complete
        self.closing = False # Don't permit new requires during close
        self.send_acquire()

        args = (log_queue, self.command_queue, self.response_queue)
        self.poller = multiprocessing.Process(target=self.continuous_poll,
                                              args=args)
        self.poller.start()

    def close(self):
        """ Add the poison pill to the command queue.
        """
        self.command_queue.put(None)
        self.poller.join()
        self.closing = True

    def continuous_poll(self, log_queue, command_queue, response_queue):
        """ Auto-acquire new readings from the simulated device. First setup the
        log queue handler. While waiting forever for the None poison pill on the
        command queue, continuously add 'acquire' commands and post the results
        on the response queue.
        """

        applog.process_log_configure(log_queue)

        self.device = SimulateSpectra()

        # Read forever until the None poison pill is received
        while True:
            try:
                record = command_queue.get()
                if record is None:
                    log.debug("Exit command queue")
                    break

                time.sleep(0.1)
                data = self.device.read()
                log.debug("Collected data in continuous poll")
                response_queue.put(data)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                import sys, traceback
                print >> sys.stderr, 'Whoops! Problem:'
                traceback.print_exc(file=sys.stderr)

    def read(self):
        """ Don't use if queue.empty() for flow control on python 2.7 on
        windows, as it will hang. Use the catch of the queue empty exception as
        shown below instead.
        """
        if self.closing:
            log.debug("In closing - do not add new acquire")
            return None

        self.send_acquire()

        result = None
        try:
            result = self.response_queue.get_nowait()
            #log.debug("Successful read: %s", result)
            self.acquire_sent = False
        except Queue.Empty:
            pass

        return result


    def send_acquire(self):
        """ Only send one acquire onto the control queue at a time.  Requires
        that the removal of the data from the data queue resets the acquire_sent
        parameter. This is done after a succesful de-queuing in the read
        function.
        """
        if self.acquire_sent:
            return

        log.debug("Send acquire")
        self.command_queue.put("ACQUIRE")
        self.acquire_sent = True
