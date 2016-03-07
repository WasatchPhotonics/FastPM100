""" Provide a set of tests cases to demonstrate basic communication with
thorlabs pm100 usb.
"""

import zmq
import time
import pytest

from multiprocessing import Process

from PySide import QtCore, QtTest

from fastpm100 import applog, devices

@pytest.mark.skipif(not pytest.config.getoption("--network"),
                    reason="need --network option to run")
class TestZMQReads():

    def test_zmq_socket_subscribe(self):

        temp_context = zmq.Context()
        temp_socket = temp_context.socket(zmq.SUB)
        temp_socket.connect ("tcp://127.0.0.1:6545")
        temp_socket.setsockopt(zmq.SUBSCRIBE,
                               "temperatures_and_power")

    def test_zmq_get_data_from_socket(self):
        temp_context = zmq.Context()
        temp_socket = temp_context.socket(zmq.SUB)
        temp_socket.connect ("tcp://127.0.0.1:6545")
        temp_socket.setsockopt(zmq.SUBSCRIBE,
                               "temperatures_and_power")

        socket_wait = 1.0
        print "Wait %s seconds for socket" % socket_wait
        time.sleep(socket_wait)
        #string = temp_socket.recv(flags=zmq.NOBLOCK)
        string = temp_socket.recv()

        (topic, message_data) = string.split(" ")
        assert topic == "temperatures_and_power"

    def test_zmq_wrapper_device_has_read(self, caplog):
        device = devices.TriValueZMQ()
        assert "TriValueZMQ setup" in caplog.text()
        applog.explicit_log_close()

    def test_zmq_device_is_available(self, caplog):
        """ This requires the publisher exists in a separate process.
        """
        device = devices.TriValueZMQ()
        result = device.read()

        assert result != 0
        assert result != None

        applog.explicit_log_close()

    def test_zmq_single_value_is_returned(self, caplog):
        """ This requires the publisher exists in a separate process.
        """
        device = devices.TriValueZMQ()
        result = device.read()

        assert result != 0

        applog.explicit_log_close()

    def test_zmq_dual_read_has_two_values(self, caplog):
        """ This requires the publisher exists in a separate process.
        """
        device = devices.TriValueZMQ()
        temperature, power = device.dual_read()

        assert temperature != 0
        assert power != 0

        applog.explicit_log_close()
