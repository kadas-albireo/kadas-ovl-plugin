# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ovl_reader_dialog_base.ui'
#
# Created: Tue Feb 16 14:56:42 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_OvlReaderDialogBase(object):
    def setupUi(self, OvlReaderDialogBase):
        OvlReaderDialogBase.setObjectName(_fromUtf8("OvlReaderDialogBase"))
        OvlReaderDialogBase.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(OvlReaderDialogBase)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.filepathLE = QtGui.QLineEdit(OvlReaderDialogBase)
        self.filepathLE.setObjectName(_fromUtf8("filepathLE"))
        self.horizontalLayout.addWidget(self.filepathLE)
        self.filesearchPB = QtGui.QPushButton(OvlReaderDialogBase)
        self.filesearchPB.setObjectName(_fromUtf8("filesearchPB"))
        self.horizontalLayout.addWidget(self.filesearchPB)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(OvlReaderDialogBase)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(OvlReaderDialogBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), OvlReaderDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(OvlReaderDialogBase)

    def retranslateUi(self, OvlReaderDialogBase):
        OvlReaderDialogBase.setWindowTitle(_translate("OvlReaderDialogBase", "Ovl Reader", None))
        self.filesearchPB.setText(_translate("OvlReaderDialogBase", "PushButton", None))

