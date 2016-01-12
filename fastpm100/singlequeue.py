""" Single queue sub process control and response.
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
    def __init__(self, log_queue=None):
        self.queue = multiprocessing.Queue(maxsize=1)
        self.queue.put("Startup", block=True, timeout=1.0)

        args = (log_queue, self.queue)
        self.proc = multiprocessing.Process(target=self.run, args=args)

        self.proc.start()

    def close(self):
        try:
            self.queue.put(None, block=True, timeout=1.0)
        except Queue.Full:
            log.critical("Can't put poison pill on queue")

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            import sys, traceback
            print >> sys.stderr, 'Whoops! Problem:'
            traceback.print_exc(file=sys.stderr)


        self.proc.join(0.1)
        self.proc.terminate()
        log.debug("Post proc terminate")

    def run(self, log_queue, queue):
        applog.process_log_configure(log_queue)

        self.device = devices.SimulatedPM100()
        self.total_reads = 0

        while True:
            try:
                result = queue.get(block=True, timeout=2.0)
                if result is None:
                    log.critical("Poison pill received, exit")
                    log.critical("Total reads: %s", self.total_reads)
                    break

                result = self.device.read()
                self.total_reads += 1
                res_tuple = (self.total_reads, result)
                queue.put(res_tuple, block=True, timeout=2.0)

            except Queue.Full:
                log.critical("Should never happen - queue full")

            except Queue.Empty:
                log.critical("Should never get to this empty queue")

            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                import sys, traceback
                print >> sys.stderr, 'Whoops! Problem:'
                traceback.print_exc(file=sys.stderr)


        log.debug("Outside main run, exiting")


    def read(self):
        """ Don't use if queue.empty() for flow control on python 2.7 on
        windows, as it will hang. Use the catch of the queue empty exception as
        shown below instead.
        """
        result = None
        try:
            result = self.queue.get(block=True, timeout=1.5)
            #log.debug("Successful read of %s", result)

            # Now put something back on the queue to make sure the main loop
            # does not require a timeout
            self.queue.put("from read", timeout=1.5)

        except Queue.Empty:
            log.debug("queue empty exception on queue get in read")
            pass

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            import sys, traceback
            print >> sys.stderr, 'Whoops! Problem:'
            traceback.print_exc(file=sys.stderr)

        return result

