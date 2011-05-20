import logging
import urllib2
from PyQt4.QtGui import QDialog, QFrame
from PyQt4.QtCore import QObject, SIGNAL, SLOT
from ui.addblogui import Ui_AddBlogDialog 
from core.blogmanager import getBlogManager, RubriqueBlogSetupError, UnknownPlatform

log = logging.getLogger("rubrique")
connect = QObject.connect
class AddBlogDialog(QDialog, Ui_AddBlogDialog):
    def __init__(self):
        QDialog.__init__(self)
        Ui_AddBlogDialog.__init__(self)

        self.setupUi(self)
        connect(self.addBlogButtonBox, SIGNAL("accepted()"), self.verifyAndAddBlog) #AddBlogDialog.accept)
        connect(self.addBlogButtonBox, SIGNAL("rejected()"), self.reject)#AddBlogDialog.reject)

    def getData(self):
        data = {}
        data['url'] = str(self.blogurltxt.text())
        data['password'] = str(self.passwordtxt.text())
        data['username'] = str(self.usernametxt.text())
        if self.addBlogAdvGroupBox.isChecked():
            data['endpoint'] = str(self.endpointtxt.text())
            data['api'] = str(self.apicombo.currentText())
        return data

    def setWarning(self, message):
        self.setStatus(message, level="warning")

    def setStatus(self, message, level="warning"):
        if level == 'warning':
            self.warninglbl.setFrameStyle(QFrame.Panel | QFrame.Sunken);
            self.warninglbl.setWordWrap(True)
            self.warninglbl.setText("<i><font color='red'>%s</font></i>" % message)

    def verifyAndAddBlog(self):
        if not self.verifyData(): return
        data = self.getData()
        url, username, password = data['url'], data['username'], data['password']
        if 'endpoint' in data:
            endpoint = data['endpoint']
        else:
            endpoint = None
        if 'api' in data:
            api = data['api']
        else:
            api = None
        log.info("User Input Data: url:%s, username:%s, password:%s, api:%s, endpoint:%s" %(url, username, password, api, endpoint))
        blogManager = getBlogManager()
        try:
            newblog = blogManager.resolve_blog(url, username, password)
            blogManager.set_current_blog(newblog.rubrique_key)
            self.accept()
        #TODO asking for and resolving endpoints
        except RubriqueBlogSetupError,e:
           addBlogDialog.setWarning(str(e))
        except UnknownPlatform, e:
           addBlogDialog.setWarning(str(e))

 
    def verifyData(self):
        missing_info = []
        errormsgs = []
        data = self.getData()
        for key, value in data.iteritems():
            if not value:
                missing_info.append(key)
        if missing_info:
            errormsgs.append("The following information is missing. Please provide them: " + ", ".join(missing_info)+'.')
        if not checkUrl(data['url']):
            errormsgs.append("The url '%s' is not found." %data['url'])
        if 'endpoint' in data and not checkUrl(data['endpoint']):
            errormsgs.append("The endpoint '%s' is not found." %data['endpoint'])
        if errormsgs:
            self.setWarning(" ".join(errormsgs))
            return False
        else:
            return True

addBlogDialog = None
def addNewBlog():
    global addBlogDialog
    if not addBlogDialog:
        addBlogDialog = AddBlogDialog()
    if addBlogDialog.exec_():
        return True
    else:
        return False

#!/usr/bin/env python
def checkUrl(url):
    try:
        request = urllib2.Request(url)
        request.get_method = lambda : 'HEAD'
        response = urllib2.urlopen(request)
        return response.code != 404
    except:
        return False 

if __name__=="__main__":
    print checkUrl("http://www.example.com") # True
    print checkUrl("http://www.example.com/nothing.html") # False
 
