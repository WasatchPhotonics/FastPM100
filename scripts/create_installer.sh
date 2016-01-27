#!/bin/bash
#
# Freeze the application code with pyinstaller, create the windows
# installer with InnoSetup.  This is designed to be run in git-bash on
# windows. Appveyor.yml uses a similar configuration to control
# continuous integration builds.


pyinstaller \
    --distpath=scripts/built-dist \
    --workpath=scripts/work-path \
    --noconfirm \
    --clean \
    --windowed \
    --icon fastpm100/assets/images/ApplicationIcon.ico \
    --specpath scripts \
    scripts/FastPM100.py

/c/Program\ Files\ \(x86\)/Inno\ Setup\ 5/iscc.exe scripts/Application_InnoSetup.iss
