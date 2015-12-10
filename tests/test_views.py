""" tests for gui layout using pyside
"""

import pytest
from PySide import QtCore, QtTest

from fastpm100 import views

import sys
import logging
log = logging.getLogger()
strm = logging.StreamHandler(sys.stderr)
frmt = logging.Formatter("%(name)s - %(levelname)s %(message)s")
strm.setFormatter(frmt)
log.addHandler(strm)
log.setLevel(logging.DEBUG)

class TestSingleNumberLayout:

    @pytest.fixture
    def my_form(self, qtbot):
        log.debug("Setup fixture")
        new_form = views.SingleNumber()
        return new_form

    def visualization_wait(self, my_form, qtbot, timeout=1000):
        signal = my_form.customContextMenuRequested
        with qtbot.wait_signal(signal, timeout=timeout):
            my_form.show()

    def test_form_has_single_power_number(self, my_form, qtbot):
        QtTest.QTest.qWaitForWindowShown(my_form)
        self.visualization_wait(my_form, qtbot)

        assert my_form.lbl_info.text() == "FastPM100"
        assert my_form.width() == 640
        assert my_form.height() == 500

    def test_form_button_click_changes_label(self, my_form, qtbot):
        QtTest.QTest.qWaitForWindowShown(my_form)
        self.visualization_wait(my_form, qtbot)

        assert my_form.button.text() == "Change Text"
        assert my_form.lbl_info.text() == "FastPM100"

        qtbot.mouseClick(my_form.button, QtCore.Qt.LeftButton)

        assert my_form.lbl_info.text() == "Button clicked"

