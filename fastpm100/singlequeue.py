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
        self.total_clear_good = 0
        self.total_clear_fail = 0
        self.total_put_good = 0
        self.total_put_fail = 0

        while True:
            if not self.clear_and_control(queue):
                log.debug("Break on poison pill")
                break

            self.read_and_put(queue, self.device)

        log.debug("Outside main run, exiting")

    def clear_and_control(self, queue):
        try:
            result = queue.get(block=True, timeout=0.1)
            self.total_clear_good += 1

            if result is None:
                log.debug("None detected on queue")
                log.debug("Clear Good %s, Fail %s", self.total_clear_good, self.total_clear_fail)
                log.debug("Put Good %s, Fail %s", self.total_put_good, self.total_put_fail)
                return False

        except Queue.Empty:
            #log.debug("Queue is empty, on clear and control")
            self.total_clear_fail += 1
            pass

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            import sys, traceback
            print >> sys.stderr, 'Whoops! Problem:'
            traceback.print_exc(file=sys.stderr)

        return True

    def read_and_put(self, queue, device):

        try:
            result = device.read()
            self.total_reads += 1

            res_tuple = (self.total_reads, result)
            queue.put(res_tuple, block=True, timeout=1.5)
            self.total_put_good += 1

        except Queue.Full:
            # This can happen if the close command puts the poison pill on the
            # queue in the small window between clearing the queue and putting
            # new data on.
            #log.debug("PUT queue full exception on put timeout")
            self.total_put_fail += 1
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
        except Queue.Empty:
            log.critical("Queue empty exception on queue get in read")
            pass

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            import sys, traceback
            print >> sys.stderr, 'Whoops! Problem:'
            traceback.print_exc(file=sys.stderr)

        return result

