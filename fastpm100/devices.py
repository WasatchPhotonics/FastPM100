""" Simulated device components for demonstration program. Simple blocking calls
with simulated delays for simulated spectrometer readings. Long-polling
multiprocessing wrappers.
"""

import time
import Queue
import numpy
import logging
import multiprocessing

from . import applog

log = logging.getLogger(__name__)


class SimulatedPM100(object):
    """ Create a simulated laser power output meter.
    """
    def __init__(self, noise_factor=1.0):
        super(SimulatedPM100, self).__init__()
        log.debug("%s setup", self.__class__.__name__)

        self.noise_factor = noise_factor

    def read(self):
        """ Return a single value with noise applied.
        """
        value = 123.0
        value = value + numpy.random.uniform(0, self.noise_factor, 1)
        value = value[0]
        #log.debug("Return: %s" % value)
        return value

class LongPollingSimulatedPM100(object):
    """ Wrap simulate pm100 in a non-blocking interface run in a separate
    process.
    """
    def __init__(self, log_queue=None, auto_acquire=None):
        self.response_queue = multiprocessing.Queue()
        self.command_queue = multiprocessing.Queue()

        self.auto_acquire = auto_acquire
        self.acquire_sent = False # Wait for an acquire to complete
        self.closing = False # Don't permit new requires during close
        self.send_acquire()

        args = (log_queue,
                self.command_queue, self.response_queue,
                self.auto_acquire)
        self.poller = multiprocessing.Process(target=self.continuous_poll,
                                              args=args)
        self.poller.start()

    def close(self):
        """ Add the poison pill to the command queue.
        """
        self.command_queue.put(None)
        self.poller.join()
        self.closing = True

    def continuous_poll(self, log_queue,
                        command_queue, response_queue,
                        auto_acquire):
        """ Auto-acquire new readings from the simulated device. First setup the
        log queue handler. While waiting forever for the None poison pill on the
        command queue, continuously add 'acquire' commands and post the results
        on the response queue.
        """

        applog.process_log_configure(log_queue)

        self.device = SimulatedPM100()

        total_reads = 0
        # Read forever until the None poison pill is received
        while True:
            try:
                record = command_queue.get_nowait()
                if record is None:
                    log.debug("Exit command queue")
                    break

                time.sleep(0.0001)
                data = self.device.read()
                total_reads += 1
                log.debug("Collected data in continuous poll %s" % total_reads)
                response_queue.put(data)

                #if auto_acquire:
                    #command_queue.put("auto acquire")

            except Queue.Empty:
                #log.debug("Queue empty")
                time.sleep(0.0001)
                data = self.device.read()
                total_reads += 1
                log.debug("Collected data in continuous poll %s" % total_reads)
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

        #log.debug("Send acquire")
        self.command_queue.put("ACQUIRE")
        self.acquire_sent = True
