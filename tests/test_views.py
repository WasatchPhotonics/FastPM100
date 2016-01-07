""" Provide a set of tests cases to demonstrate a basic gui that meets
wasatch needs. This includes menu bar, buttons, and text controls. Verify that
logging from the views with default setup is available to the capturelog
fixture.
"""

import pytest

from PySide import QtCore, QtTest

from fastpm100 import views

class TestBasicWindow:

    @pytest.fixture(scope="function")
    def strip_form(self, qtbot, request):
        """ Create the view at every setup, close it on final.
        """
        new_form = views.StripWindow()

        def form_close():
            new_form.close()
        request.addfinalizer(form_close)

        return new_form

    def test_form_has_default_setup(self, strip_form, qtbot):
        assert strip_form.ui.labelMinimum.text() == "0.0"
        assert strip_form.width() == 1080
        assert strip_form.height() == 418

    def test_form_has_pyqtgraph_widget(self, strip_form, qtbot):
        assert strip_form.ui.plot.width() == 856
        assert strip_form.ui.plot.height() == 400

    @pytest.fixture(scope="function")
    def my_form(self, qtbot, request):
        """ Create the new QMainWindow from the view at every test
        setup.
        """
        new_form = views.BasicWindow()

        # Close the form when the test ends
        def form_close():
            new_form.close()
        request.addfinalizer(form_close)

        return new_form

    def test_form_has_text_and_button_controls(self, my_form, qtbot):
        QtTest.QTest.qWaitForWindowShown(my_form)

        assert my_form.lbl_info.text() == "Application Default"
        assert my_form.width() == 400
        assert my_form.height() == 400

    def test_form_button_click_changes_label(self, my_form, qtbot):
        QtTest.QTest.qWaitForWindowShown(my_form)

        assert my_form.button.text() == "Change Text"
        assert my_form.lbl_info.text() == "Application Default"

        qtbot.mouseClick(my_form.button, QtCore.Qt.LeftButton)

        # For debugging the application events, use wait to let you see the
        # contents of the form
        qtbot.wait(1000)

        assert "Button clicked" in my_form.lbl_info.text()

    def test_direct_logging_is_available(self, my_form, qtbot, caplog):
        QtTest.QTest.qWaitForWindowShown(my_form)
        qtbot.mouseClick(my_form.button, QtCore.Qt.LeftButton)

        qtbot.wait(1000)
        assert "Button clicked" in caplog.text()

    def test_close_view_triggers_custom_signal(self, my_form, caplog, qtbot):
        """ Control script reads from close event triggered by GUI close event,
        such as the user clicking the window X. This test ensures that that
        signal is available.
        """
        QtTest.QTest.qWaitForWindowShown(my_form)

        signal = my_form.exit_signal.exit
        timeout = 3
        with qtbot.wait_signal(signal, timeout=timeout):
            my_form.close()

        assert "View level close" in caplog.text()
