# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'background.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


import json
from PyQt5 import QtCore, QtGui, QtWidgets

with open('setting.json', 'r+') as f_obj:
    set_dict = json.load(f_obj)


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(302, 662)
        o = (100-set_dict['win_opacity_spin'])/100
        Form.setWindowOpacity(o)  # 设置窗口透明度
        if set_dict['stay']:
            Form.setWindowFlags(QtCore.Qt.WindowDoesNotAcceptFocus |
                                QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        else:
            Form.setWindowFlags(QtCore.Qt.WindowDoesNotAcceptFocus |
                                QtCore.Qt.FramelessWindowHint)

        """self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(250, 100, 251, 231))
        self.label.setStyleSheet("background-color: rgb(160, 0, 0);\n"
                                 "font: 75 9pt \"Arial Narrow\";\n"
                                 "font: 75 9pt \"微软雅黑\";\n"
                                 "font: 75 9pt \"微软雅黑\";\n"
                                 "text-decoration: underline;\n"
                                 "font: 9pt \"微软雅黑\";")
        self.label.setObjectName("label")"""
        op = QtWidgets.QGraphicsOpacityEffect()
        o = (100-set_dict['obj_opacity_spin'])/100
        op.setOpacity(o)  # 设置组件透明度
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(730, 40, 75, 23))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        """
        self.label.setText(_translate("Form", "TextFontLabel"))"""
        self.pushButton.setText(_translate("Form", "PushButton"))
