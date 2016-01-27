# FastPM100
High speed acquisition and visualization of ThorLabs PM100 power meter
readings.

[![Travis Build Status](https://travis-ci.org/WasatchPhotonics/FastPM100.svg?branch=master)](https://travis-ci.org/WasatchPhotonics/FastPM100?branch=master)
[![Appveyor Build Status](https://ci.appveyor.com/api/projects/status/ruqnlbwuwl31lp6n/branch/master?svg=true)](https://ci.appveyor.com/project/NathanHarrington/FastPM100)
[![Coverage Status](https://coveralls.io/repos/WasatchPhotonics/FastPM100/badge.svg?branch=master&service=github)](https://coveralls.io/github/WasatchPhotonics/FastPM100?branch=master)

Specifications for the Thorlabs PM100 class laser power meters include
3000 acquisitions per second. This project is designed to show all 3k
readings per second to the user for low pulse width laser power
measurements.

FastPM100 provides two different modes of visualization:

    Basic strip chart
        Shows the last 3k readings and the current reading.

    Experimental visualization
        Heatmaps, multi line plots and other techniques to help
        visualize short duration laser power measurements.




Running tests:

    First, install the python package in development mode:
        python setup.py develop

    All Tests, with coverage report showing missing lines:
        py.test tests/ --cov=fastpm100 --cov-report term-missing

    Certain tests are marked xfail to pass without access to the
    physical hardware. After the setup is performed below, run these
    with:

    py.test tests/test_thorlabs.py --hardware

Setup access to physical hardware:

    sudo -e /etc/udev/rules.d/99-thorlabs.rules

Add the following text:

    # Thorlabs PM100 USB
    SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="1313", ATTRS{idProduct}=="8072", MODE="0666"

