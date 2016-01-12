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
            if not self.clear_and_control(queue):
                log.debug("Break on poison pill")
                break

            self.read_and_put(queue, self.device)

        log.debug("Outside main run, exiting")

    def clear_and_control(self, queue):
        try:
            result = queue.get(block=False)

            if result is None:
                log.debug("None detected on queue")
                return False
        except Queue.Empty:
            #log.debug("Queue is empty, on clear and control")
            pass

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            import sys, traceback
            print >> sys.stderr, 'Whoops! Problem:'
            traceback.print_exc(file=sys.stderr)

        return True

    def read_and_put(self, queue, device):
        sleep_wait = 0.1

        try:
            result = device.read()
            self.total_reads += 1

            res_tuple = (self.total_reads, result)
            #log.debug("Add to queue: %s, %s" % res_tuple)
            #queue.put(res_tuple, block=True, timeout=0.1)
            queue.put(res_tuple, block=False)
            #log.debug("Succesfully added to queue, wait %s", sleep_wait)
            #time.sleep(sleep_wait)

        except Queue.Full:
            #log.debug("PUT queue full exception on put timeout")
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
            result = self.queue.get(block=True, timeout=1.5)
            #log.debug("Successful read of %s", result)
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

