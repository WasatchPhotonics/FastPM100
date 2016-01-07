#!/bin/bash
#
# Freeze the application code with py2exe, create the windows installer
# with InnoSetup. 

python scripts/py2exe_application.py py2exe
/c/Program\ Files\ \(x86\)/Inno\ Setup\ 5/iscc.exe scripts/Application_InnoSetup.iss

