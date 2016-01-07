""" Controller tests that show the linkage between the data model, view, and
logging components.
Mimic the contents of the scripts/FastPM100.py setup section. Create the logger
with the queue handler as part of the test case, as opposed to having the
controller create the top level logger
"""

import time
import pytest

from PySide import QtTest

from fastpm100 import control
from fastpm100 import applog


class TestControl:

    def test_control_logs_visible_to_caplog(self, caplog, qtbot):
        main_logger = applog.MainLogger()

        app_control = control.Controller(main_logger.log_queue)
        qtbot.wait(1000)

        app_control.close()
        time.sleep(1)

        main_logger.close()
        time.sleep(1)
        assert "Control startup" in caplog.text()
        applog.explicit_log_close()


    def test_view_logs_visible_to_caplog(self, caplog, qtbot):
        main_logger = applog.MainLogger()

        app_control = control.Controller(main_logger.log_queue)
        qtbot.wait(1000)

        app_control.close()
        time.sleep(1)

        main_logger.close()
        time.sleep(1)
        assert "Init of StripWindow" in caplog.text()
        applog.explicit_log_close()

    def test_device_logs_in_file_only(self, caplog, qtbot):
        """ Shows the expected behavior. Demonstrates that the capturelog
        fixture on py.test does not see sub process entries.
        """
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()

        app_control = control.Controller(main_logger.log_queue)
        qtbot.wait(1000)

        app_control.close()
        time.sleep(1)

        main_logger.close()
        time.sleep(1)

        log_text = applog.get_text_from_log()
        assert "SimulatedPM100 setup" in log_text
        assert "SimulatedPM100 setup" not in caplog.text()
        applog.explicit_log_close()


    def test_close_view_emits_control_signal(self, caplog, qtbot):
        """ Control script emits an event on a close condition to be processsed
        by the parent qt application, in this case qtbot. In the scripts file,
        it's the Qapplication.
        """
        main_logger = applog.MainLogger()
        app_control = control.Controller(main_logger.log_queue)

        QtTest.QTest.qWaitForWindowShown(app_control.form)

        signal = app_control.control_exit_signal.exit
        with qtbot.wait_signal(signal, timeout=1):
            app_control.form.close()

        main_logger.close()
        time.sleep(1)
        assert "Control level close" in caplog.text()
        applog.explicit_log_close()

    def test_simulated_device_updates_current_value(self, caplog, qtbot):
        main_logger = applog.MainLogger()
        app_control = control.Controller(main_logger.log_queue)

        QtTest.QTest.qWaitForWindowShown(app_control.form)

        signal = app_control.control_exit_signal.exit
        qtbot.wait(1000)
        first_val = app_control.form.ui.labelCurrent.text()

        qtbot.wait(1000)
        second_val = app_control.form.ui.labelCurrent.text()
        assert first_val != second_val

        app_control.close()
        main_logger.close()
        applog.explicit_log_close()

    @pytest.fixture(scope="function")
    def simulate_main(self, qtbot, request):
        """ Setup the controller the same way the scripts/Application does at
        every setup. Ensure that the teardown is in place regardless of test
        result.
        """
        main_logger = applog.MainLogger()
        app_control = control.Controller(main_logger.log_queue)

        def control_close():
            app_control.close()
            main_logger.close()
            applog.explicit_log_close()

        request.addfinalizer(control_close)

        return app_control

    def test_simulated_device_updates_graph(self, simulate_main, qtbot):

        qtbot.wait(1000)

        points = simulate_main.form.curve.getData()
        first_point = points[1][-1]

        qtbot.wait(1000)

        points = simulate_main.form.curve.getData()
        second_point = points[1][-1]

        assert first_point != second_point
