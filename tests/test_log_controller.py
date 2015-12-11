""" Simulating tests to verify that multiprocessing + pyside and pytest-qt
configuration can print log files correctly.
"""

import sys
import time

import logging
log = logging.getLogger()
strm = logging.StreamHandler(sys.stderr)
frmt = logging.Formatter("%(name)s - %(levelname)s %(message)s")
strm.setFormatter(frmt)
log.addHandler(strm)
log.setLevel(logging.DEBUG)

#import multiprocessing
#multiprocessing.log_to_stderr(logging.DEBUG)

class TestLogWithPySideAndPyTestQt:

    def test_control_object_with_sub_logger(self, qtbot):
        from fastpm100 import control
        control = control.AppExam()

        signal = control.form.customContextMenuRequested
        with qtbot.wait_signal(signal, timeout=3000):
            control.form.show()

        assert True == False

