""" Provide a set of tests cases to demonstrate a basic gui that meets
wasatch needs. This includes menu bar, buttons, and text controls. Verify that
logging from the views with default setup is available to the capturelog
fixture.
"""

import pytest

from PySide import QtCore, QtTest

from fastpm100 import views

@pytest.mark.skipif(pytest.config.getoption("--appveyor"),
                    reason="need --appveyor option to disable tests")
class TestStripChart:

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
        assert strip_form.width() >= 900
        assert strip_form.height() >= 318

    def test_form_has_pyqtgraph_widget(self, strip_form, qtbot):
        assert strip_form.ui.plot.width() >= 700
        assert strip_form.ui.plot.height() >= 300

    def test_form_has_toolbar_action_buttons(self, strip_form, qtbot):
        strip_wfo = strip_form.ui.toolBar.widgetForAction
        widget = strip_wfo(strip_form.ui.actionPause)
        assert widget.width() >= 24
        assert widget.height() >= 24

        widget = strip_wfo(strip_form.ui.actionContinue)
        assert widget.width() >= 24
        assert widget.height() >= 24



@pytest.mark.skipif(pytest.config.getoption("--appveyor"),
                    reason="need --appveyor option to disable tests")
class TestBlueGraphSkin:

    @pytest.fixture(scope="function")
    def strip_form(self, qtbot, request):
        """ Create the view at every setup, close it on final.
        """
        new_form = views.BlueGraphStripChart()

        def form_close():
            new_form.close()
        request.addfinalizer(form_close)

        return new_form

    def test_form_has_default_setup(self, strip_form, qtbot):
        assert strip_form.ui.labelMinimum.text() == "0.0"
        assert strip_form.width() >= 900
        assert strip_form.height() >= 318

    def test_form_has_pyqtgraph_widget(self, strip_form, qtbot):
        assert strip_form.ui.plot.width() >= 700
        assert strip_form.ui.plot.height() >= 300

    def test_form_has_toolbar_action_buttons(self, strip_form, qtbot):
        strip_wfo = strip_form.ui.toolBar.widgetForAction
        widget = strip_wfo(strip_form.ui.actionPause)
        assert widget.width() >= 24
        assert widget.height() >= 24

        widget = strip_wfo(strip_form.ui.actionContinue)
        assert widget.width() >= 24
        assert widget.height() >= 24

@pytest.mark.skipif(pytest.config.getoption("--appveyor"),
                    reason="need --appveyor option to disable tests")
class TestDualAxisStripChart:

    @pytest.fixture(scope="function")
    def strip_form(self, qtbot, request):
        """ Create the view at every setup, close it on final.
        """
        new_form = views.DualStripWindow()

        def form_close():
            new_form.close()
        request.addfinalizer(form_close)

        return new_form

    def test_form_has_default_setup(self, strip_form, qtbot):
        assert strip_form.ui.labelMinimum.text() == "0.0"
        assert strip_form.width() >= 900
        assert strip_form.height() >= 318

        qtbot.wait(5000)


class TestAllStripWindow:

    @pytest.fixture(scope="function")
    def strip_form(self, qtbot, request):
        """ Create the view at every setup, close it on final.
        """
        new_form = views.AllStripWindow()

        def form_close():
            new_form.close()
        request.addfinalizer(form_close)

        return new_form

    def test_form_has_default_setup(self, strip_form, qtbot):
        assert strip_form.ui.labelMinimum.text() == "0.0"
        assert strip_form.width() >= 900
        assert strip_form.height() >= 318

        qtbot.wait(3000)

