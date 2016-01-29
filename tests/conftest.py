""" From: https://pytest.org/latest/example/simple.html, add a command
line switch to run the tests that require power meter hardware. This is
to isolate any log file processing issues.
"""

import pytest
def pytest_addoption(parser):
    parser.addoption("--hardware", action="store_true",
        help="run tests requiring physical hardware")
    parser.addoption("--appveyor", action="store_true",
        help="disable tests that are known to break on appveyor")
