# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fastpm100/assets/component_toggle_strip_layout.ui'
#
# Created: Fri Mar 11 09:40:06 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(946, 452)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.stackedWidget = QtGui.QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtGui.QWidget()
        self.page.setObjectName("page")
        self.label = QtGui.QLabel(self.page)
        self.label.setGeometry(QtCore.QRect(150, 200, 341, 16))
        self.label.setObjectName("label")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName("page_2")
        self.stackedWidget.addWidget(self.page_2)
        self.horizontalLayout.addWidget(self.stackedWidget)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_9 = QtGui.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.frameRight = QtGui.QFrame(self.centralwidget)
        self.frameRight.setMinimumSize(QtCore.QSize(175, 200))
        self.frameRight.setMaximumSize(QtCore.QSize(150, 200))
        self.frameRight.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameRight.setFrameShadow(QtGui.QFrame.Raised)
        self.frameRight.setObjectName("frameRight")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.frameRight)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_8 = QtGui.QLabel(self.frameRight)
        self.label_8.setMinimumSize(QtCore.QSize(60, 0))
        self.label_8.setObjectName("label_8")
        self.verticalLayout_4.addWidget(self.label_8)
        self.label_9 = QtGui.QLabel(self.frameRight)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_4.addWidget(self.label_9)
        self.label_10 = QtGui.QLabel(self.frameRight)
        self.label_10.setObjectName("label_10")
        self.verticalLayout_4.addWidget(self.label_10)
        self.horizontalLayout_8.addLayout(self.verticalLayout_4)
        self.verticalLayout_6 = QtGui.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.labelCurrent = QtGui.QLabel(self.frameRight)
        self.labelCurrent.setMinimumSize(QtCore.QSize(70, 0))
        self.labelCurrent.setObjectName("labelCurrent")
        self.verticalLayout_6.addWidget(self.labelCurrent)
        self.labelMinimum = QtGui.QLabel(self.frameRight)
        self.labelMinimum.setObjectName("labelMinimum")
        self.verticalLayout_6.addWidget(self.labelMinimum)
        self.labelMaximum = QtGui.QLabel(self.frameRight)
        self.labelMaximum.setObjectName("labelMaximum")
        self.verticalLayout_6.addWidget(self.labelMaximum)
        self.horizontalLayout_8.addLayout(self.verticalLayout_6)
        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.verticalLayout_5.addLayout(self.verticalLayout_3)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_6 = QtGui.QLabel(self.frameRight)
        self.label_6.setMinimumSize(QtCore.QSize(60, 0))
        self.label_6.setObjectName("label_6")
        self.verticalLayout_2.addWidget(self.label_6)
        self.label_7 = QtGui.QLabel(self.frameRight)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_2.addWidget(self.label_7)
        self.label_3 = QtGui.QLabel(self.frameRight)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.horizontalLayout_7.addLayout(self.verticalLayout_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelRenderFPS = QtGui.QLabel(self.frameRight)
        self.labelRenderFPS.setMinimumSize(QtCore.QSize(70, 0))
        self.labelRenderFPS.setObjectName("labelRenderFPS")
        self.verticalLayout.addWidget(self.labelRenderFPS)
        self.labelDataFPS = QtGui.QLabel(self.frameRight)
        self.labelDataFPS.setObjectName("labelDataFPS")
        self.verticalLayout.addWidget(self.labelDataFPS)
        self.labelSkipFPS = QtGui.QLabel(self.frameRight)
        self.labelSkipFPS.setObjectName("labelSkipFPS")
        self.verticalLayout.addWidget(self.labelSkipFPS)
        self.horizontalLayout_7.addLayout(self.verticalLayout)
        self.verticalLayout_5.addLayout(self.horizontalLayout_7)
        self.verticalLayout_9.addWidget(self.frameRight)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_9.addItem(spacerItem)
        self.horizontalLayout_2.addLayout(self.verticalLayout_9)
        MainWindow.setCentralWidget(self.centralwidget)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionPause = QtGui.QAction(MainWindow)
        self.actionPause.setCheckable(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/ui/images/greys/pause.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPause.setIcon(icon)
        self.actionPause.setObjectName("actionPause")
        self.actionContinue = QtGui.QAction(MainWindow)
        self.actionContinue.setCheckable(True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/ui/images/greys/forward.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.actionContinue.setIcon(icon1)
        self.actionContinue.setObjectName("actionContinue")
        self.actionCCD_Temp = QtGui.QAction(MainWindow)
        self.actionCCD_Temp.setCheckable(True)
        self.actionCCD_Temp.setObjectName("actionCCD_Temp")
        self.actionLaser_Temp = QtGui.QAction(MainWindow)
        self.actionLaser_Temp.setCheckable(True)
        self.actionLaser_Temp.setObjectName("actionLaser_Temp")
        self.actionLaser_Power = QtGui.QAction(MainWindow)
        self.actionLaser_Power.setCheckable(True)
        self.actionLaser_Power.setObjectName("actionLaser_Power")
        self.actionYellow_Therm = QtGui.QAction(MainWindow)
        self.actionYellow_Therm.setCheckable(True)
        self.actionYellow_Therm.setObjectName("actionYellow_Therm")
        self.actionBlue_Therm = QtGui.QAction(MainWindow)
        self.actionBlue_Therm.setCheckable(True)
        self.actionBlue_Therm.setObjectName("actionBlue_Therm")
        self.actionAmps = QtGui.QAction(MainWindow)
        self.actionAmps.setCheckable(True)
        self.actionAmps.setObjectName("actionAmps")
        self.toolBar.addAction(self.actionContinue)
        self.toolBar.addAction(self.actionPause)
        self.toolBar.addAction(self.actionLaser_Temp)
        self.toolBar.addAction(self.actionCCD_Temp)
        self.toolBar.addAction(self.actionYellow_Therm)
        self.toolBar.addAction(self.actionBlue_Therm)
        self.toolBar.addAction(self.actionAmps)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Primary Stacked widget", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("MainWindow", "Current", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("MainWindow", "Minimum", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("MainWindow", "Maximum", None, QtGui.QApplication.UnicodeUTF8))
        self.labelCurrent.setText(QtGui.QApplication.translate("MainWindow", "0.0", None, QtGui.QApplication.UnicodeUTF8))
        self.labelMinimum.setText(QtGui.QApplication.translate("MainWindow", "0.0", None, QtGui.QApplication.UnicodeUTF8))
        self.labelMaximum.setText(QtGui.QApplication.translate("MainWindow", "0.0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("MainWindow", "Render/Sec", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("MainWindow", "Data/Sec", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("MainWindow", "Skip/Sec", None, QtGui.QApplication.UnicodeUTF8))
        self.labelRenderFPS.setText(QtGui.QApplication.translate("MainWindow", "0.0", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDataFPS.setText(QtGui.QApplication.translate("MainWindow", "0.0", None, QtGui.QApplication.UnicodeUTF8))
        self.labelSkipFPS.setText(QtGui.QApplication.translate("MainWindow", "0.0", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPause.setText(QtGui.QApplication.translate("MainWindow", "Pause", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPause.setToolTip(QtGui.QApplication.translate("MainWindow", "Pause gray updates", None, QtGui.QApplication.UnicodeUTF8))
        self.actionContinue.setText(QtGui.QApplication.translate("MainWindow", "Continue", None, QtGui.QApplication.UnicodeUTF8))
        self.actionContinue.setToolTip(QtGui.QApplication.translate("MainWindow", "Continue live graph updates", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCCD_Temp.setText(QtGui.QApplication.translate("MainWindow", "CCD Temp", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLaser_Temp.setText(QtGui.QApplication.translate("MainWindow", "Laser Temp", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLaser_Power.setText(QtGui.QApplication.translate("MainWindow", "Laser Power", None, QtGui.QApplication.UnicodeUTF8))
        self.actionYellow_Therm.setText(QtGui.QApplication.translate("MainWindow", "Yellow Therm", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBlue_Therm.setText(QtGui.QApplication.translate("MainWindow", "Blue Therm", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAmps.setText(QtGui.QApplication.translate("MainWindow", "Amps", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc