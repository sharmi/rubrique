# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_resources/chooseblog.ui'
#
# Created: Sun May 22 15:52:02 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ChooseBlogDialog(object):
    def setupUi(self, ChooseBlogDialog):
        ChooseBlogDialog.setObjectName(_fromUtf8("ChooseBlogDialog"))
        ChooseBlogDialog.resize(640, 480)
        ChooseBlogDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(ChooseBlogDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.chooseBlogFrame = QtGui.QFrame(ChooseBlogDialog)
        self.chooseBlogFrame.setFrameShape(QtGui.QFrame.Panel)
        self.chooseBlogFrame.setFrameShadow(QtGui.QFrame.Sunken)
        self.chooseBlogFrame.setObjectName(_fromUtf8("chooseBlogFrame"))
        self.verticalLayout.addWidget(self.chooseBlogFrame)
        self.chooseBlogButtonBox = QtGui.QDialogButtonBox(ChooseBlogDialog)
        self.chooseBlogButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.chooseBlogButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.chooseBlogButtonBox.setObjectName(_fromUtf8("chooseBlogButtonBox"))
        self.verticalLayout.addWidget(self.chooseBlogButtonBox)

        self.retranslateUi(ChooseBlogDialog)
        QtCore.QMetaObject.connectSlotsByName(ChooseBlogDialog)

    def retranslateUi(self, ChooseBlogDialog):
        ChooseBlogDialog.setWindowTitle(QtGui.QApplication.translate("ChooseBlogDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

