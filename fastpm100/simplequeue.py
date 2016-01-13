""" Use queue empty and full checks instead of exception catching for clearer
and hopefully faster communications on windows and linux.
"""


from multiprocessing import Queue as MPQueue
from multiprocessing import Process

from fastpm100 import applog

import logging
log = logging.getLogger(__name__)

class SubProcess(object):
    def __init__(self, log_queue):
        log.debug("%s startup", __name__)

        self.results = MPQueue(maxsize=1)

        self.control = MPQueue(maxsize=1)

        args = (log_queue, self.results, self.control)
        self.proc = Process(target=self.run, args=args)
        self.proc.start()

    def run(self, log_queue, results, control):

        applog.process_log_configure(log_queue)
        read_count = 0

        while True:
            log.debug("Main loop")

            if control.full():
                log.debug("Data on control queue, exiting")
                break

            if results.empty():
                log.debug("Put data on queue")
                results.put((read_count, 123.0))

            read_count +=1

        log.debug("End of run while")

    def close(self):
        log.debug("%s close", __name__)

        log.debug("Add none to control poison pill")
        self.control.put(None, block=True, timeout=1.0)

        self.proc.join(0.1)
        self.proc.terminate()
        log.debug("Close completion post terminate")


    def read(self):
        log.debug("%s read", __name__)
        get_result = self.results.get(block=True, timeout=1.0)
        return get_result

