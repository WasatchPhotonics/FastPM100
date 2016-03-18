""" Simulated device components for demonstration program. Simple blocking calls
with simulated delays for simulated spectrometer readings. Long-polling
multiprocessing wrappers.
"""

import sys
import time
import logging
import platform

import zmq
import visa
import serial

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
        """ Read off the publisher queue, return just the spectrometer
        temps and laser power
        """
        string = self.socket.recv()
        values = string.split(" ")[1]

        ccd_temp = values.split(",")[0]
        laser_temp = values.split(",")[1]
        laser_power = values.split(",")[2]

        return float(ccd_temp), float(laser_temp), float(laser_power)

class DualTriValueZMQ(TriValueZMQ):
    """ Read three values off a zmq publisher queue with a subscriber
    interface, wrap in the "read" nomenclature for use in the fastpm100
    type visualization. Return laser temperature and pm100 laser power.
    """
    def __init__(self, *args, **kwargs):
        super(DualTriValueZMQ, self).__init__(*args, **kwargs)

        log.debug("%s setup", self.__class__.__name__)

    def read(self):
        """ Like read above, return a tuple in combined_log order of average
        laser temp, average laser power.
        """

        string = self.socket.recv()
        values = string.split(" ")[1]

        ltemp_value = values.split(",")[-2]
        power_value = values.split(",")[-1]

        return float(ltemp_value), float(power_value)


class AllValueZMQ(TriValueZMQ):
    """ Read the entire string off the zmq publisher queue, split the
    values by a space and return as a tuple. Wrap with the "read"
    nomenclature for use in the FastPM100 multiprocessing wrapper.
    """
    def __init__(self, *args, **kwargs):
        super(AllValueZMQ, self).__init__(*args, **kwargs)

        log.debug("%s setup", self.__class__.__name__)

    def read(self):
        """ Like read above, return a tuple in combined_log order of average
        laser temp, average laser power.
        """

        string = self.socket.recv()
        values = string.split(" ")[1]

        float_values = []
        for item in values.split(","):
            float_values.append(float(item))

        return float_values


class SlapChopDevice(object):
    """ Communicate over a virtual com port on windows, send the
    acquisition command and receive three values comma delimited.
    Yellow (thermistor), Blue and current.
    """

    def __init__(self):
        log.debug("%s setup", self.__class__.__name__)

        self.com_port = "COM3" # As of 2016-03-08 10:06, pip serial
        # expects the com port string as reported by windows

        self.serial_port = serial.Serial()
        self.serial_port.baudrate = 115200
        self.serial_port.port = self.com_port
        self.serial_port.timeout = 1
        self.serial_port.writeTimeout = 1

        try:
            result = self.serial_port.close() # yes, close before open
            result = self.serial_port.open()
        except Exception as exc:
            log.critical("Problem close/open: %s", exc)
            raise exc

    def read(self):
        result = self.write_command("s")
        result = result.replace('\r\n','')
        result = result.replace(',','')
        temp_yellow = result.split(" ")[0]
        temp_blue = result.split(" ")[1]
        amps = result.split(" ")[2]
        return float(temp_yellow), float(temp_blue), float(amps)


    def write_command(self, command, read_bytes=24):
        """ append required control characters to the specified command,
        write to the device over the serial port, and expect the number
        of bytes returned.
        """

        result = None
        try:
            fin_command = command + '\n'
            log.debug("send command [%s]", fin_command)
            result = self.serial_port.write(str(fin_command))
            self.serial_port.flush()
        except Exception as exc:
            log.critical("Problem writing to port: %s", exc)
            return result

        try:
            result = self.serial_port.read(read_bytes)
            log.debug("Serial read result [%r]" % result)

        except Exception as exc:
            log.critical("Problem reading from port: %s", exc)
            return result

        log.debug("command write/read successful")
        return result


