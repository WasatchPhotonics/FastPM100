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

import logging
log = logging.getLogger()
strm = logging.StreamHandler(sys.stderr)
frmt = logging.Formatter("%(asctime)s %(name)s - %(levelname)s %(message)s")
strm.setFormatter(frmt)
log.addHandler(strm)
log.setLevel(logging.DEBUG)


import signal
def signal_handler(signal, frame):
    print("pressed Ctrl+C!")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

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
