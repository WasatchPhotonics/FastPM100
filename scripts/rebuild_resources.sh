#!/bin/bash
#
# Run supporting pyrcc files to generate resource files and future
# designer conversions into python code. Run this from the home project
# directory like:
# ./scripts/rebuild_resources.sh

CMD_NAME="pyside-rcc"
UIC_NAME="pyside-uic"


if [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    echo "Windows detected"
    # pdm-works computer
    #CMD_NAME="C:\Python27\Lib\site-packages\PySide\pyside-rcc.exe"
    #UIC_NAME="C:\Python27\Lib\site-packages\PySide\pyside-uic.exe"
    # microwave computer
    CMD_NAME="C:\Python27\Lib\site-packages\PySide\pyside-rcc.exe"
    UIC_NAME="C:\Python27\scripts\pyside-uic.exe"
fi

echo "Rebuilding resources file"
# Use the relative package name glob so the build is portable across
# other projects
$CMD_NAME \
    */assets/resources.qrc \
    -o */assets/resources_rc.py


echo "Rebuilding uic forms"
$UIC_NAME \
    fastpm100/assets/strip_layout.ui \
    -o fastpm100/assets/strip_layout.py
