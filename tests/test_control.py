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


    def test_simulated_device_updates_graph(self, simulate_main, qtbot):


        QtTest.QTest.qWaitForWindowShown(simulate_main.form)
        #qtbot.wait(6000)
        with qtbot.waitSignal(signal=None, timeout=3000):
            print "wait instead of qtbot wait"

        points = simulate_main.form.curve.getData()
        print "points: ", points
        first_point = points[1][-1]

        #qtbot.wait(6000)

        with qtbot.waitSignal(signal=None, timeout=3000):
            print "wait instead of qtbot wait"
        points = simulate_main.form.curve.getData()
        print "second points: ", points
        second_point = points[1][-1]

        assert first_point != second_point
