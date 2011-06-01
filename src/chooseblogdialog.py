import logging
from PyQt4.QtGui import QDialog, QFrame, QVBoxLayout, QRadioButton, QButtonGroup, QMessageBox
from PyQt4.QtCore import QObject, SIGNAL, SLOT
from ui.chooseblog_ui import Ui_ChooseBlogDialog 

log = logging.getLogger("rubrique")
connect = QObject.connect

class BlogRadio(QRadioButton):
    def __init__(self, *args):
        QRadioButton.__init__(self, *args[:-1])
        self.blog = args[-1]

class ChooseBlogDialog(QDialog, Ui_ChooseBlogDialog):
    def __init__(self, available_blogs, addToDB):
        QDialog.__init__(self)
        Ui_ChooseBlogDialog.__init__(self)
        self.func = addToDB
        self.setupUi(self)
        radioboxLayout = QVBoxLayout()
        self.radiobuttonGroup = QButtonGroup()
        self.radios = []
        for blog in available_blogs:
            radio = BlogRadio("Blog Title: %s,   Url: %s" %(blog.blogname, blog.homeurl), blog)
            self.radiobuttonGroup.addButton(radio)
            radioboxLayout.addWidget(radio)
            self.radios.append(radio)
        self.chooseBlogFrame.setLayout(radioboxLayout)
        self.adjustSize()
        connect(self.chooseBlogButtonBox, SIGNAL("accepted()"), self.addBlog) #AddBlogDialog.accept)
        connect(self.chooseBlogButtonBox, SIGNAL("rejected()"), self.reject)#AddBlogDialog.reject)

    def addBlog(self):
        if self.radiobuttonGroup.checkedButton():
            self.func(self.radiobuttonGroup.checkedButton().blog)
            self.accept()
        else:
            QMessageBox.warning(self, "Choose A Blog", "Please choose a blog and click OK.  If you do not want to add a blog, Please click 'Cancel'", QMessageBox.Ok, QMessageBox.Ok)
        pass

