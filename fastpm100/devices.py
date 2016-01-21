""" Simulated device components for demonstration program. Simple blocking calls
with simulated delays for simulated spectrometer readings. Long-polling
multiprocessing wrappers.
"""

import visa
import time
import numpy
import logging
import platform

from ThorlabsPM100 import ThorlabsPM100, USBTMC

from . import applog

log = logging.getLogger(__name__)


class ThorlabsMeter(object):
    """ Create a simulated laser power output meter.
    """
    def __init__(self, noise_factor=1.0):
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
        print "Dev list", dev_list
        #if dev_list:
            #log.debug("Device list: %r" % dev_list)

        device = resource_man.open_resource(dev_list[0])
        log.debug("Created visa device: %r" % device)
        print("Created visa device: %r" % device)

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
        if self.linux:
            return self.power_meter.read
        else:
            result = self.power_meter.ask("MEAS:POW?\n")
            return float(result)

class SimulatedPM100(object):
    """ Create a simulated laser power output meter.
    """
    def __init__(self, noise_factor=1.0, sleep_factor=None):
        super(SimulatedPM100, self).__init__()
        log.debug("%s setup", self.__class__.__name__)

        self.noise_factor = noise_factor
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
