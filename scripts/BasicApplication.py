#!/usr/bin/python
""" Bare bones application designed to show multiprocessing,
PySide, logging, windows and linux support. Also be distributable
with py2exe and Innosetup.
"""

import sys
import time
import multiprocessing

from PySide import QtGui, QtCore

from fastpm100 import views
from fastpm100 import devices
from fastpm100 import log_helpers

import logging
log = logging.getLogger()
frmt = logging.Formatter("%(asctime)s %(name)s - %(levelname)s %(message)s")
log.setLevel(logging.DEBUG)

# Add a stderr output handler for the application
#strm = logging.StreamHandler(sys.stderr)
strm = logging.StreamHandler(sys.stdout)
strm.setFormatter(frmt)
log.addHandler(strm)


# Add a file handler for the application
log_dir = log_helpers.get_location()
log_dir += "/BasicApplication_log.txt"

file_handler = logging.FileHandler(log_dir)
file_handler.setFormatter(frmt)
log.addHandler(file_handler)


def main():
    # Required on ms windows
    multiprocessing.freeze_support()

    app = QtGui.QApplication(sys.argv)
    ex = views.SingleNumber()

    mp_device = devices.QueueMPDevice()
    mp_device.create()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
