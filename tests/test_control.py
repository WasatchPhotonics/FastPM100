""" Controller tests that show the linkage between the data model, view, and
logging components.
Mimic the contents of the scripts/FastPM100.py setup section. Create the logger
with the queue handler as part of the test case, as opposed to having the
controller create the top level logger
"""

import time
import pytest

from PySide import QtTest

from fastpm100 import control, applog


class TestControl:

    @pytest.fixture(scope="function")
    def simulate_main(self, qtbot, request):
        """ Setup the controller the same way the scripts/Application does at
        every setup. Ensure that the teardown is in place regardless of test
        result.
        """
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()
        app_control = control.Controller(main_logger.log_queue)

        qtbot.addWidget(app_control.form)

        def control_close():
            app_control.close()
            main_logger.close()
            applog.explicit_log_close()

        request.addfinalizer(control_close)

        return app_control

    def test_control_logs_visible_to_caplog(self, simulate_main, caplog, qtbot):
        QtTest.QTest.qWaitForWindowShown(simulate_main.form)
        assert "Control startup" in caplog.text()

    def test_view_logs_visible_to_caplog(self, simulate_main, caplog, qtbot):
        QtTest.QTest.qWaitForWindowShown(simulate_main.form)
        assert "Init of StripWindow" in caplog.text()

    def test_device_logs_in_file_only(self, simulate_main, caplog, qtbot):
        """ Shows the expected behavior. Demonstrates that the capturelog
        fixture on py.test does not see sub process entries.
        """
        QtTest.QTest.qWaitForWindowShown(simulate_main.form)
        qtbot.wait(1000)

        log_text = applog.get_text_from_log()
        assert "SimulatedPM100 setup" in log_text
        assert "SimulatedPM100 setup" not in caplog.text()

    def test_close_view_emits_control_signal(self, simulate_main, caplog, qtbot):
        """ Control script emits an event on a close condition to be processsed
        by the parent qt application, in this case qtbot. In the scripts file,
        it's the Qapplication.
        """

        QtTest.QTest.qWaitForWindowShown(simulate_main.form)
        qtbot.wait(1000)

        close_signal = simulate_main.control_exit_signal.exit
        with qtbot.wait_signal(close_signal, timeout=1):
            simulate_main.form.close()

        time.sleep(1)
        assert "Control level close" in caplog.text()

    def test_simulated_device_updates_current_value(self, simulate_main, caplog, qtbot):

        QtTest.QTest.qWaitForWindowShown(simulate_main.form)

        qtbot.wait(1000)
        first_val = simulate_main.form.ui.labelCurrent.text()

        qtbot.wait(1000)
        second_val = simulate_main.form.ui.labelCurrent.text()

        assert first_val != second_val


    def test_simulated_device_updates_graph(self, simulate_main, qtbot):
        QtTest.QTest.qWaitForWindowShown(simulate_main.form)

        qtbot.wait(1000)
        points = simulate_main.form.curve.getData()
        first_point = points[1][-1]

        qtbot.wait(1000)
        points = simulate_main.form.curve.getData()
        second_point = points[1][-1]

        assert first_point != second_point

    def test_min_max_update(self, simulate_main, qtbot):

        qtbot.wait(1000)
        min_val = simulate_main.form.ui.labelMinimum.text()
        assert min_val != "0.0"

        max_val = simulate_main.form.ui.labelMaximum.text()
        assert max_val != "0.0"

    def test_dfps_rfps_update(self, simulate_main, qtbot):
        qtbot.wait(1000)
        dfps_val = simulate_main.form.ui.labelDFPS.text()
        assert dfps_val != "0.0"

        rfps_val = simulate_main.form.ui.labelRFPS.text()
        assert rfps_val != "0.0"

