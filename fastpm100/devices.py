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
        self.counter = 0.1234567

    def read(self):
        """ Return a single value with noise applied.
        """
        value = 123.0 + numpy.random.uniform(0, self.noise_factor, 1)
        value = value[0]
        #log.debug("Return: %s" % value)
        return value

class SubProcessSimulatedPM100(object):
    """ Wrap simulate pm100 in a non-blocking interface run in a separate
    process.
    """
    def __init__(self, log_queue=None):
        self.response_queue = multiprocessing.Queue()
        self.command_queue = multiprocessing.Queue()

        args = (log_queue, self.command_queue, self.response_queue)
        self.poller = multiprocessing.Process(target=self.continuous_poll,
                                              args=args)
        self.poller.start()

    def close(self):
        """ Add the poison pill to the command queue.
        """
        self.command_queue.put(None)
        self.poller.join(1)     # Required on Windows
        self.poller.terminate() # Required on windows
        log.debug("Post poller terminate")

    def continuous_poll(self, log_queue, command_queue, response_queue):

        applog.process_log_configure(log_queue)

        self.device = SimulatedPM100()

        total_reads = 0
        # Read forever until the None poison pill is received
        while True:

            data = self.device.read()
            total_reads += 1
            response_queue.put_nowait((total_reads, data))
            time.sleep(0.0001)
            #log.debug("Collected data in continuous poll %s" % total_reads)

            try:
                record = command_queue.get_nowait()
                if record is None:
                    log.debug("Exit command queue")
                    break

            except Queue.Empty:
                #log.debug("Queue empty")
                #time.sleep(0.1001)
                pass

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
        result = None
        try:
            result = self.response_queue.get_nowait()
        except Queue.Empty:
            pass

        return result

