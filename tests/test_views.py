""" tests for gui layout using pyside
"""

import pytest
from PySide import QtCore, QtTest

from fastpm100 import views

class TestSingleNumberLayout:

    @pytest.fixture
    def my_form(self, qtbot):
        new_form = views.SingleNumber()
        return new_form

    def test_form_has_single_power_number(self, my_form, qtbot):
        QtTest.QTest.qWaitForWindowShown(my_form)

        signal = my_form.customContextMenuRequested
        with qtbot.wait_signal(signal, timeout=2000):
            my_form.show()

        assert my_form.lbl_info.text() == "FastPM100"
        assert my_form.width() == 640
        assert my_form.height() == 500
