# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_resources/addblog.ui'
#
# Created: Mon May  9 11:26:28 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_AddBlogDialog(object):
    def setupUi(self, AddBlogDialog):
        AddBlogDialog.setObjectName(_fromUtf8("AddBlogDialog"))
        AddBlogDialog.resize(421, 480)
        self.gridLayout = QtGui.QGridLayout(AddBlogDialog)
        self.gridLayout.setSpacing(20)
        self.gridLayout.setContentsMargins(18, 20, -1, -1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.blogurllbl = QtGui.QLabel(AddBlogDialog)
        self.blogurllbl.setObjectName(_fromUtf8("blogurllbl"))
        self.gridLayout.addWidget(self.blogurllbl, 1, 0, 1, 1)
        self.blogurltxt = QtGui.QLineEdit(AddBlogDialog)
        self.blogurltxt.setObjectName(_fromUtf8("blogurltxt"))
        self.gridLayout.addWidget(self.blogurltxt, 1, 1, 1, 1)
        self.usernamelbl = QtGui.QLabel(AddBlogDialog)
        self.usernamelbl.setObjectName(_fromUtf8("usernamelbl"))
        self.gridLayout.addWidget(self.usernamelbl, 2, 0, 1, 1)
        self.usernametxt = QtGui.QLineEdit(AddBlogDialog)
        self.usernametxt.setObjectName(_fromUtf8("usernametxt"))
        self.gridLayout.addWidget(self.usernametxt, 2, 1, 1, 1)
        self.passwordlbl = QtGui.QLabel(AddBlogDialog)
        self.passwordlbl.setObjectName(_fromUtf8("passwordlbl"))
        self.gridLayout.addWidget(self.passwordlbl, 3, 0, 1, 1)
        self.passwordtxt = QtGui.QLineEdit(AddBlogDialog)
        self.passwordtxt.setObjectName(_fromUtf8("passwordtxt"))
        self.gridLayout.addWidget(self.passwordtxt, 3, 1, 1, 1)
        self.line = QtGui.QFrame(AddBlogDialog)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 4, 0, 1, 2)
        self.addBlogAdvGroupBox = QtGui.QGroupBox(AddBlogDialog)
        self.addBlogAdvGroupBox.setFlat(False)
        self.addBlogAdvGroupBox.setCheckable(True)
        self.addBlogAdvGroupBox.setChecked(False)
        self.addBlogAdvGroupBox.setObjectName(_fromUtf8("addBlogAdvGroupBox"))
        self.formLayout = QtGui.QFormLayout(self.addBlogAdvGroupBox)
        self.formLayout.setContentsMargins(20, 20, -1, -1)
        self.formLayout.setSpacing(20)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.apilbl = QtGui.QLabel(self.addBlogAdvGroupBox)
        self.apilbl.setObjectName(_fromUtf8("apilbl"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.apilbl)
        self.apicombo = QtGui.QComboBox(self.addBlogAdvGroupBox)
        self.apicombo.setObjectName(_fromUtf8("apicombo"))
        self.apicombo.addItem(_fromUtf8(""))
        self.apicombo.addItem(_fromUtf8(""))
        self.apicombo.addItem(_fromUtf8(""))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.apicombo)
        self.endpoinlbl = QtGui.QLabel(self.addBlogAdvGroupBox)
        self.endpoinlbl.setObjectName(_fromUtf8("endpoinlbl"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.endpoinlbl)
        self.endpointtxt = QtGui.QLineEdit(self.addBlogAdvGroupBox)
        self.endpointtxt.setObjectName(_fromUtf8("endpointtxt"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.endpointtxt)
        self.gridLayout.addWidget(self.addBlogAdvGroupBox, 5, 0, 1, 2)
        self.addBlogButtonBox = QtGui.QDialogButtonBox(AddBlogDialog)
        self.addBlogButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.addBlogButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.addBlogButtonBox.setObjectName(_fromUtf8("addBlogButtonBox"))
        self.gridLayout.addWidget(self.addBlogButtonBox, 7, 0, 1, 2)
        self.warninglbl = QtGui.QLabel(AddBlogDialog)
        self.warninglbl.setText(_fromUtf8(""))
        self.warninglbl.setObjectName(_fromUtf8("warninglbl"))
        self.gridLayout.addWidget(self.warninglbl, 6, 0, 1, 2)

        self.retranslateUi(AddBlogDialog)
        QtCore.QMetaObject.connectSlotsByName(AddBlogDialog)

    def retranslateUi(self, AddBlogDialog):
        AddBlogDialog.setWindowTitle(QtGui.QApplication.translate("AddBlogDialog", "Add New Blog", None, QtGui.QApplication.UnicodeUTF8))
        self.blogurllbl.setText(QtGui.QApplication.translate("AddBlogDialog", "Blog Url", None, QtGui.QApplication.UnicodeUTF8))
        self.usernamelbl.setText(QtGui.QApplication.translate("AddBlogDialog", "Username", None, QtGui.QApplication.UnicodeUTF8))
        self.passwordlbl.setText(QtGui.QApplication.translate("AddBlogDialog", "Password", None, QtGui.QApplication.UnicodeUTF8))
        self.addBlogAdvGroupBox.setTitle(QtGui.QApplication.translate("AddBlogDialog", "Advanced", None, QtGui.QApplication.UnicodeUTF8))
        self.apilbl.setText(QtGui.QApplication.translate("AddBlogDialog", "Supported API", None, QtGui.QApplication.UnicodeUTF8))
        self.apicombo.setItemText(0, QtGui.QApplication.translate("AddBlogDialog", "MetaWeblog", None, QtGui.QApplication.UnicodeUTF8))
        self.apicombo.setItemText(1, QtGui.QApplication.translate("AddBlogDialog", "Atom", None, QtGui.QApplication.UnicodeUTF8))
        self.apicombo.setItemText(2, QtGui.QApplication.translate("AddBlogDialog", "Blogger", None, QtGui.QApplication.UnicodeUTF8))
        self.endpoinlbl.setText(QtGui.QApplication.translate("AddBlogDialog", "EndPoint", None, QtGui.QApplication.UnicodeUTF8))

