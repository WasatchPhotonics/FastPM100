""" Use queue empty and full checks instead of exception catching for clearer
and hopefully faster communications on windows and linux.
"""

import logging
from multiprocessing import Queue as MPQueue

log = logging.getLogger(__name__)

class SubProcess(object):
    def __init__(self, loq_queue):
        log.debug("%s startup", __name__)

        self.results = MPQueue(maxsize=1)
        self.results.put((1, "Startup"), block=True, timeout=1.0)

    def close(self):
        log.debug("%s close", __name__)


    def read(self):
        log.debug("%s read", __name__)
        get_result = self.results.get(block=True, timeout=1.0)
        return get_result

