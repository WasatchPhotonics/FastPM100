""" single objects used in by pytest-qt or the main controlling script
to create views and link data sources with functions.
"""

import logging
log = logging.getLogger(__name__)
log.debug("module level init")

from fastpm100 import views
from fastpm100 import devices


class AppExam(object):
    def __init__(self):
        log.debug("init")
        super(AppExam, self).__init__()

        self.form = views.SingleNumber()
        self.device = devices.QueueMPDevice()
        self.device.create()

