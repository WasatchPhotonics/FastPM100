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
        qtbot.wait(1000)
        assert "Control startup" in caplog.text()

    def test_view_logs_visible_to_caplog(self, simulate_main, caplog, qtbot):
        qtbot.wait(1000)
        assert "Init of StripWindow" in caplog.text()
