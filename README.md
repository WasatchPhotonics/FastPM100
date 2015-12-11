# FastPM100
High speed acquisition and visualization of ThorLabs PM100 power meter readings


In addition, this project is released at various stages providing a
serires of bare bones functionality. Support for continuous integration
environments with cross platform PySide testability. Also included is
multiprocessing with logging across windows and linux. Deployable
applications with build instructions and InnoSetup packages.


Now it appears that the log issues with the multiprocessing setup is an
issue with the py.test run. If you run the basic application directly or
build it as an executable with the default log setups, the log prints
seem to appear fine. It's only if you run the py.test
tests/test_log_controller.py -s  that the log prints do not show up to
stderr. If it truly is just the test scripts on windows, then fix that.
Figure out how to determine if running under pytest on windows, then
re-create the logger in each process.

This is not the same as having a centralized logger to handle file
rotation and to ensure correct order. May have to add that later.

Also building the exe proceeds fine, but when run gives the message:

File "PySide\_utils.pyc", line 63, in _get_win32_short_name
WindowsError: [Error 3] The system cannot find the path specified.

That can be addressed by the mechanisms here:
http://stackoverflow.com/questions/17509088/system-path-error-with-pyqt-and-py2exe


Also taking a calculated risk with the exclusion of the msvcp90.dll and
any other MS runtime dll. Excluding these in the py2exe setup file is
based on years of experience with the Dash installer code base where I
the lack of that file has come up once. In about 4 years of development,
on an unpatched winxp 64 machine, I believe.
