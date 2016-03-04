""" Simulated device components for demonstration program. Simple blocking calls
with simulated delays for simulated spectrometer readings. Long-polling
multiprocessing wrappers.
"""

import time
import logging
import platform

import zmq
import visa

from ThorlabsPM100 import ThorlabsPM100, USBTMC

log = logging.getLogger(__name__)


class ThorlabsMeter(object):
    """ Create a simulated laser power output meter.
    """
    def __init__(self):
        super(ThorlabsMeter, self).__init__()
        log.debug("%s setup", self.__class__.__name__)

        if "Linux" in platform.platform():
            self.linux = True
            self.power_meter = self.create_usbtmc()
        else:
            self.linux = False
            self.power_meter = self.create_visa()

    def create_visa(self):
        """ Use VISA to create a connection to the thorlabs pm100usb
        power meter on windows. See FastPM100/Readme.md for details on
        setup.
        """
        resource_man = visa.ResourceManager()
        dev_list = resource_man.list_resources()
        log.debug("Dev list %s", dev_list)

        device = resource_man.open_resource(dev_list[0])
        log.debug("Created visa device: %s", device)

        return device

    def create_usbtmc(self):
        """ Use USBTMC to create a connection to the thorlabs pm100usb
        on linux.
        """
        self.inst = USBTMC(device="/dev/usbtmc0")
        power_meter = ThorlabsPM100(inst=self.inst)
        power_meter.sense.correction.wavelength = 785.0
        return power_meter

    def read(self):
        """ Perform the expected USBTMC or visa acquisition from the device.
        """
        if self.linux:
            result = float(self.power_meter.read) * 1000.0
            return result
        else:
            result = self.power_meter.ask("MEAS:POW?\n")
            result = float(result) * 1000.0
            return float(result)

class SimulatedPM100(object):
    """ Create a simulated laser power output meter.
    """
    def __init__(self, sleep_factor=None):
        super(SimulatedPM100, self).__init__()
        log.debug("%s setup", self.__class__.__name__)

        self.counter = 0.1234567
        self.sleep_factor = sleep_factor

    def increment_counter(self):
        """ Add a value to return value.
        """
        self.counter += 0.000001
        value = 123.0 + self.counter
        if self.sleep_factor is not None:
            time.sleep(self.sleep_factor)
        return value

    def read(self):
        """ Return the test-specific pattern.
        """
        return self.increment_counter()

class TriValueZMQ(object):
    """ Read three values off a zmq publisher queue with a subscriber
    interface, wrap in the "read" nomenclature for use in the fastpm100
    type visualization.
    """
    def __init__(self, ip_address="127.0.0.1", port="6545",
                 topic="temperatures_and_power"):
        super(TriValueZMQ, self).__init__()
        log.debug("%s setup", self.__class__.__name__)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)

        connect_str = "tcp://%s:%s" % (ip_address, port)
        log.debug("Connecting to: %s, topic: %s", connect_str, topic)
        self.socket.connect(connect_str)
        self.socket.setsockopt(zmq.SUBSCRIBE, topic)

        socket_wait = 1.0
        log.debug("Wait %s seconds for socket", socket_wait)
        time.sleep(socket_wait)

    def read(self):
        """ Read off the publisher queue, return the result as a string.
        """
        string = self.socket.recv()
        values = string.split(" ")[1]
        power_value = values.split(",")[-1]

        return float(power_value)

