""" BlueGraph - application control for visualization of data.
"""

import sys
import logging
import argparse
import multiprocessing

from PySide import QtGui, QtCore

from fastpm100 import control
from fastpm100 import applog

log = logging.getLogger(__name__)

import signal
def signal_handler(signal, frame):
        log.critical('You pressed Ctrl+C!')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

class FastPM100Application(object):
    """ Create the window with the graphs, setup communication based on
    the specified device.
    """
    def __init__(self):
        super(FastPM100Application, self).__init__()
        log.debug("startup")
        self.parser = self.create_parser()
        self.form = None
        self.args = None

    def parse_args(self, argv):
        """ Handle any bad arguments, then set defaults.
        """
        log.debug("Process args: %s", argv)
        self.args = self.parser.parse_args(argv)
        return self.args

    def create_parser(self):
        """ Create the parser with arguments specific to this
        application.
        """
        desc = "acquire from specified device, display line graph"
        parser = argparse.ArgumentParser(description=desc)

        help_str = "Automatically terminate the program for testing"
        parser.add_argument("-t", "--testing", action="store_true",
                            help=help_str)
        return parser

    def run(self):
        """ This is the application code that is called by the main
        function. The architectural idea is to have as little code in
        main as possible and create the qapplication here so the
        testing code can function separately with pytest-qt.
        """
        self.app = QtGui.QApplication([])

        self.main_logger = applog.MainLogger()
        app_control = control.Controller(self.main_logger.log_queue,
                                         device_name="SimulatedPM100",
                                         history_size=3000)

        app_control.control_exit_signal.exit.connect(self.closeEvent)

        sys.exit(self.app.exec_())


    def closeEvent(self):
        """ catch the exit signal from the control application, and
        call qapplication Quit. This will prevent hangs on exit.
        """
        log.debug("Application quit")
        self.main_logger.close()
        self.app.quit()

def main(argv=None):
    """ main calls the wrapper code around the application objects with
    as little framework as possible. See:
    https://groups.google.com/d/msg/comp.lang.python/j_tFS3uUFBY/\
        ciA7xQMe6TMJ
    """
    argv = argv[1:]
    log.debug("Arguments: %s", argv)

    exit_code = 0
    print "Application exec"
    try:
        go_app = FastPM100Application()
        go_app.parse_args(argv)
        go_app.run()

    except SystemExit, exc:
        exit_code = exc.code

    return exit_code

if __name__ == "__main__":
    multiprocessing.freeze_support()
    sys.exit(main(sys.argv))
