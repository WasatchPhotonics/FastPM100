#!/usr/bin/python

from PySide import QtGui, QtCore

import sys
import time

import logging
log = logging.getLogger()
strm = logging.StreamHandler(sys.stderr)
frmt = logging.Formatter("%(name)s - %(levelname)s %(message)s")
strm.setFormatter(frmt)
log.addHandler(strm)
log.setLevel(logging.DEBUG)



import signal
def signal_handler(signal, frame):
    print("pressed Ctrl+C!")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def main():

    app = QtGui.QApplication(sys.argv)
    from fastpm100 import views
    ex = views.SingleNumber()

    from fastpm100 import devices
    mp_device = devices.QueueMPDevice()
    mp_device.create()


    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
