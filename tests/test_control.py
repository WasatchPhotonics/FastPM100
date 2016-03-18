""" Controller tests that show the linkage between the data model, view, and
logging components.
Mimic the contents of the scripts/FastPM100.py setup section. Create the logger
with the queue handler as part of the test case, as opposed to having the
controller create the top level logger
"""

import time
import pytest

from PySide import QtTest, QtCore

from fastpm100 import control, applog


@pytest.mark.skipif(pytest.config.getoption("--appveyor"),
                    reason="need --appveyor option to disable tests")
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
        assert "Init" in caplog.text()

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

    def test_fps_metrics_update(self, simulate_main, qtbot):
        qtbot.wait(1000)
        dfps_val = simulate_main.form.ui.labelDataFPS.text()
        assert dfps_val != "0.0"

        rfps_val = simulate_main.form.ui.labelRenderFPS.text()
        assert rfps_val != "0.0"

        sfps_val = simulate_main.form.ui.labelSkipFPS.text()
        assert sfps_val != "0.0"

    def test_toolbar_button_status_on_startup(self, simulate_main, qtbot):

        QtTest.QTest.qWaitForWindowShown(simulate_main.form)

        check_stat = simulate_main.form.ui.actionContinue.isChecked()
        assert check_stat == True

        pause_stat = simulate_main.form.ui.actionPause.isChecked()
        assert pause_stat == False

    def test_pause_action_stops_live_update_of_graph(self, simulate_main, qtbot):

        QtTest.QTest.qWaitForWindowShown(simulate_main.form)
        smfu_wfo = simulate_main.form.ui.toolBar.widgetForAction

        act_pause = simulate_main.form.ui.actionPause
        act_continue = simulate_main.form.ui.actionContinue

        qtbot.wait(300)
        act_pause_widget = smfu_wfo(act_pause)
        qtbot.mouseClick(act_pause_widget, QtCore.Qt.LeftButton)

        assert act_continue.isChecked() == False
        assert act_pause.isChecked() == True

        # Get some data, wait then get the same positional data from the graph
        # and make sure it has not changed

        points = simulate_main.form.curve.getData()
        first_point = points[1][-1]
        qtbot.wait(300)

        points = simulate_main.form.curve.getData()
        second_point = points[1][-1]

        assert first_point == second_point

    def test_continue_action_restarts_graph(self, simulate_main, qtbot):

        QtTest.QTest.qWaitForWindowShown(simulate_main.form)
        smfu_wfo = simulate_main.form.ui.toolBar.widgetForAction

        act_pause = simulate_main.form.ui.actionPause
        act_continue = simulate_main.form.ui.actionContinue

        qtbot.wait(300)
        act_pause_widget = smfu_wfo(act_pause)
        qtbot.mouseClick(act_pause_widget, QtCore.Qt.LeftButton)
        assert act_pause.isChecked() == True
        assert act_continue.isChecked() == False

        # Data is now paused,
        points = simulate_main.form.curve.getData()
        first_point = points[1][-1]
        qtbot.wait(300)

        act_continue_widget = smfu_wfo(act_continue)
        qtbot.mouseClick(act_continue_widget, QtCore.Qt.LeftButton)
        assert act_continue.isChecked() == True
        qtbot.wait(300)

        points = simulate_main.form.curve.getData()
        second_point = points[1][-1]
        assert first_point != second_point

@pytest.mark.skipif(pytest.config.getoption("--appveyor"),
                    reason="need --appveyor option to disable tests")
class TestDualControl:

    @pytest.fixture(scope="function")
    def simulate_dual_main(self, qtbot, request):
        """ Setup the controller the same way the scripts/Application does at
        every setup. Ensure that the teardown is in place regardless of test
        result. Use the Dual controller to display two lines of data.
        """
        assert applog.delete_log_file_if_exists() == True

        main_logger = applog.MainLogger()
        app_control = control.DualController(main_logger.log_queue,
                                             device_name="DualTriValueZMQ")

        qtbot.addWidget(app_control.form)

        def control_close():
            app_control.close()
            main_logger.close()
            applog.explicit_log_close()

        request.addfinalizer(control_close)

        return app_control


    def test_close_view_emits_control_signal(self, simulate_dual_main, caplog, qtbot):
        """ Control script emits an event on a close condition to be processsed
        by the parent qt application, in this case qtbot. In the scripts file,
        it's the Qapplication.
        """

        QtTest.QTest.qWaitForWindowShown(simulate_dual_main.form)
        qtbot.wait(1000)

        close_signal = simulate_dual_main.control_exit_signal.exit
        with qtbot.wait_signal(close_signal, timeout=1):
            simulate_dual_main.form.close()

        time.sleep(1)
        assert "Control level close" in caplog.text()


@pytest.mark.skipif(pytest.config.getoption("--appveyor"),
                    reason="need --appveyor option to disable tests")
class TestAllControl:

    @pytest.fixture(scope="function")
    def simulate_all_main(self, qtbot, request, filename=None,
                          update_time_interval=0,
                          history_size=3000):
        """ Setup the controller the same way the scripts/Application does at
        every setup. Ensure that the teardown is in place regardless of test
        result. Use the All controller to display six lines of data from
        the temperature logger.
        """
        assert applog.delete_log_file_if_exists() == True

        geometry = [100, 100, 800, 500]
        main_logger = applog.MainLogger()
        app_control = control.AllController(main_logger.log_queue,
                                            geometry=geometry,
                                            update_time_interval=update_time_interval,
                                            history_size=history_size,
                                            filename=filename,
                                            device_name="AllValueZMQ")

        qtbot.addWidget(app_control.form)

        def control_close():
            app_control.close()
            main_logger.close()
            applog.explicit_log_close()

        request.addfinalizer(control_close)

        return app_control

    @pytest.fixture(scope="function")
    def simulate_reload_one_day_main(self, qtbot, request):
        filename = "tests/combined_log.csv"
        return self.simulate_all_main(qtbot, request, filename=filename,
                                      update_time_interval=10000,
                                      history_size=8640)

    @pytest.fixture(scope="function")
    def simulate_reload_100days_main(self, qtbot, request):
        filename = "tests/combined_log.csv"
        return self.simulate_all_main(qtbot, request, filename=filename,
                                      update_time_interval=60000,
                                      history_size=144000)


    def test_close_view_emits_control_signal(self, simulate_all_main, caplog, qtbot):
        """ Control script emits an event on a close condition to be processsed
        by the parent qt application, in this case qtbot. In the scripts file,
        it's the Qapplication.
        """

        QtTest.QTest.qWaitForWindowShown(simulate_all_main.form)
        qtbot.wait(1000)

        close_signal = simulate_all_main.control_exit_signal.exit
        with qtbot.wait_signal(close_signal, timeout=1):
            simulate_all_main.form.close()

        time.sleep(1)
        assert "Control level close" in caplog.text()

    def test_reload_parameter_starts_populateed(self, simulate_reload_one_day_main,
                                                caplog, qtbot):
        """ Load from a provided csv file, skipping data as appropriate
        """
        QtTest.QTest.qWaitForWindowShown(simulate_reload_one_day_main.form)
        qtbot.wait(3000)


    def test_reload_100days_starts_populateed(self, simulate_reload_100days_main,
                                                caplog, qtbot):
        QtTest.QTest.qWaitForWindowShown(simulate_reload_100days_main.form)
        qtbot.wait(3000)

