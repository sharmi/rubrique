#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from urlparse import urlunsplit
from glob import glob 
from PyQt4 import QtGui, QtCore
from ui.rubrique_ui import Ui_MainWindow
from PyQt4.QtCore import QObject,  Qt, QCoreApplication, QEvent, QFile, QFileInfo, QIODevice, QLatin1Char, QLatin1String, QPoint, QRegExp, QString, QStringList, QTimer, QUrl
from PyQt4.QtGui import QWidget,  QComboBox, QSizePolicy,  QIcon,  QLabel,  QSlider, QApplication, QColorDialog, QDesktopServices, QDialog, QFileDialog, QFontDatabase, QInputDialog, QMainWindow, QMessageBox, QMouseEvent, QStyleFactory, QTreeWidgetItem, QWhatsThis
from PyQt4.QtWebKit import QWebPage, QWebView, QWebSettings
from core.blogmanager import getBlogManager
import calendar
from xml.sax.saxutils import quoteattr
import addblogdialog 

connect = QObject.connect
SIGNAL = QtCore.SIGNAL
SLOT = QtCore.SLOT
import logging, logging.handlers

# Make a global logging object.
log  = logging.getLogger("rubrique")
log.setLevel(logging.DEBUG)

# This handler writes everything to a file.
h1 = logging.FileHandler("rubrique.log")
h2 = logging.StreamHandler(sys.stdout)
f = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
h1.setFormatter(f)
h2.setFormatter(f)
h1.setLevel(logging.DEBUG)
h2.setLevel(logging.DEBUG)
log.addHandler(h1)
log.addHandler(h2)

#self.tr = QObject.self.tr
def alert(msg):
    msgbox = QMessageBox('debugmsg', msg)
    msgbox.exec_()

class Rubrique(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
    
        self.fileName = '';
        self.windowTitle = 'Rubrique';
        self.sourceDirty = True;
        self.zoomLabel = None;
        self.zoomSlider = None;
        highlighter = None;
        ui_dialog = None;
        insertHtmlDialog = None;

        # Setup the ui.
        self.setupUi(self)
        connect(self.tabWidget, SIGNAL("currentChanged(int)"), self.changeTab);
        self.resize(600, 600);
        self.blogs = {}
        #self.spacer = QWidget(self);
        #self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum);
        #self.standardToolBar.insertWidget(self.actionZoomOut, self.spacer);
        self.labelSelector=QLabel("Current Blog: ", self.standardToolBar)
        self.comboSelector=QComboBox(self.standardToolBar)
        self.comboSelector.setEditable(False)
        self.connect(self.comboSelector,
                     SIGNAL("activated(int)"),
                     self.slotCurrentBlogChanged)
        self.standardToolBar.addWidget(self.labelSelector)
        self.standardToolBar.addWidget(self.comboSelector)

        self.zoomLabel = QLabel();
        self.standardToolBar.insertWidget(self.actionZoomIn, self.zoomLabel);

        self.zoomSlider = QSlider(self);
        self.zoomSlider.setOrientation(Qt.Horizontal);
        self.zoomSlider.setMaximumWidth(150);
        self.zoomSlider.setRange(25, 400);
        self.zoomSlider.setSingleStep(25);
        self.zoomSlider.setPageStep(100);
        self.standardToolBar.insertWidget(self.actionZoomOut, self.zoomSlider);

        self.editView.setHtml(open('html/editor.html').read())
        self.codeView.setHtml(open('html/codemirrorui.html').read())
        self.editView.page().setContentEditable(False);
        self.codeView.page().setContentEditable(False);

        self.setupBlogData();

        self.editor = 0;
        
        self.editView.setFocus();
    
        self.setCurrentFileName(QString());
    
        #codedir = os.path.dirname( os.path.realpath( __file__ ) )
        codedir = determine_path()
        self.visualViewSrc = urlunsplit(('file', '', os.path.join(codedir, 'html', 'editor.html'), '', ''))
        #self.visualViewSrc = urlunsplit(('file', '', os.path.join(codedir, 'html', 'file-click-demo.html'), '', ''))
        self.htmlViewSrc =  urlunsplit(('file', '', os.path.join(codedir, 'html', 'codemirrorui.html'), '', ''))

        #if not self.load(initialFile):
        #    self.fileNew();
        settings = self.editView.page().settings()
        settings.setAttribute(QWebSettings.JavascriptEnabled, True
        )
        settings.setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
        settings = self.codeView.page().settings()
        settings.setAttribute(QWebSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
        self.editView.load(QUrl(self.visualViewSrc))
        self.codeView.load(QUrl(self.htmlViewSrc))
        self.adjustSource()
        self.setWindowModified(False)
        self.changeZoom(100)
        self.autosaveTimer = QTimer(self)
        connect(self.autosaveTimer, SIGNAL("timeout()"), self.saveBlogContent)
        self.autosaveTimer.start(2000)
        connect(self.zoomSlider, SIGNAL("valueChanged(int)"), self.changeZoom);
        connect(self.actionPublish,  SIGNAL("triggered()"), self.publish)
        connect(self.actionFileNew, SIGNAL("triggered()"), self.fileNew);
        connect(self.actionFileOpen, SIGNAL("triggered()"), self.fileOpen);
        connect(self.actionFileSave, SIGNAL("triggered()"), self.fileSave);
        connect(self.actionFileSaveAs, SIGNAL("triggered()"), self.fileSaveAs);
        connect(self.actionExit, SIGNAL("triggered()"), self.close);
        connect(self.actionZoomOut, SIGNAL("triggered()"), self.zoomOut);
        connect(self.actionZoomIn, SIGNAL("triggered()"), self.zoomIn);
        connect(self.actionAddNewBlog, SIGNAL("triggered()"), self.addNewBlog)     
        connect(self.postTitleTxt, SIGNAL("textEdited(QString)"), self.blogManager.setTitle) 
        connect(self.excerptTxt, SIGNAL("textChanged()"), self.setExcerpt)
        connect(self.trackbacksCheck, SIGNAL("stateChanged(int)"), self.blogManager.allowTrackbacks)
        connect(self.commentsCheck, SIGNAL("stateChanged(int)"), self.blogManager.allowComments)
        # Qt 4.5.0 has a bug: always returns 0 for QWebPage.SelectAll
        
    
        #necessary to sync our actions
        #connect(self.editView.page(), SIGNAL("selectionChanged()"), self.adjustActions);
    
        connect(self.editView.page(), SIGNAL("contentsChanged()"), self.adjustSource);
        connect(self.tabWidget,  SIGNAL("currentChanged(int)"),  self.syncEditors)


    def slotCurrentBlogChanged(self):
        pass

    def setExcerpt(self):
        self.blogManager.setExcerpt(self.excerptTxt.toPlainText())

    def initUIData(self):
        print self.blogManager.getTitle(), self.blogManager.getExcerpt()
        self.postTitleTxt.setText(self.blogManager.getTitle())
        self.excerptTxt.setPlainText(self.blogManager.getExcerpt())
        self.trackbacksCheck.setChecked(self.blogManager.allowTrackbacks())
        self.commentsCheck.setChecked(self.blogManager.allowComments())
    def syncEditors(self,  force=False):
        #0 -> EditView 1->CodeView 2->Preview
        currentIndex =  self.tabWidget.currentIndex()
        if currentIndex!= self.editor or force==True:
            if self.editor == 0 :
                latestData = self.getEditData()
                self.setCodeData(latestData)
                #Set Preview data
            elif self.editor == 1:
                latestData = self.getCodeData()
                self.setEditData(latestData)
            self.preView.setHtml(latestData)
            if currentIndex in [0,  1]:
               self.editor  = currentIndex
        return True
        
    def populateComboSelector(self, blog=None):
        if blog:
            self.comboSelector.addItem("%s: %s" %(blog.blogname, blog.username))
            return
        for blog in self.blogManager.blogs:
            #blog = self.blogManager.blogs[rubrique_key]
            self.comboSelector.addItem("%s: %s" %(blog.blogname, blog.username))
        return
    
    def addNewBlog(self):
        newblog = addblogdialog.addNewBlog()
        if not newblog: return
        self.populateComboSelector(self.blogManager.currentBlog)
        #self.blogManager.set_current_blog(newblog.rubrique_key)
        
    def donothing(self):
        pass
    def setupBlogData(self):
        self.blogManager = getBlogManager()
        self.populateComboSelector()
        self.initUIData()
        #self.blogManager.add_blog('wordpress', 'http://www.minvolai.com/blog/xmlrpc.php', 'sharmila', 'letmein')
        #self.populatePosts()
    
    def populatePosts(self):
        posts = self.blogManager.get_latest_posts()
        yeardict = {}
        year_month = {}
        self.postTree.setColumnCount(1)
        blueico = QIcon("images/turquoise_button.png")
        postico = QIcon("images/open_local_post.png")
        for post in posts:
            year, month = post.date[:2]
            if year not in yeardict:
                yeartree = QTreeWidgetItem(self.postTree)
                yeartree.setIcon(0,  blueico)
                yeartree.setText(0, str(year))
                yeardict[year] = yeartree
            if (year, month) not in year_month:
                monthtree = QTreeWidgetItem(yeardict[year])
                monthtree.setIcon(0,  blueico)
                monthtree.setText(0, calendar.month_name[month])
                year_month[(year, month)] = monthtree
                
            postobj = QTreeWidgetItem(year_month[(year, month)])
            postobj.setIcon(0,  postico)
            postobj.setText(0, post.title)
            postobj.setToolTip(0,  post.title + "\n Sharmi")
             

    def FORWARD_ACTION(self, action1,  action2):
        action = self.editView.pageAction(action2)
        action.setEnabled(True)
        self.connect(action1, SIGNAL("triggered()"), self.editView.pageAction(action2),  SLOT("trigger()")); 
        #self.connect(self.editView.pageAction(action2), SIGNAL("changed()"), self.adjustActions);
   
    def saveBlogContent(self):
        self.syncEditors(force=True)
        self.blogManager.setPostBody(self.getEditData())

    def publish(self):
        self.saveBlogContent()
        #post.categories = (wordpress.getCategoryIdFromName('Python'),)
        self.blogManager.publish()
        
        
    def maybeSave(self):

        if  not self.isWindowModified():
            return True;
    
        ret = QMessageBox.warning(self, self.tr(self.windowTitle),
                                   self.tr("The document has been modified.\n"
                                      "Do you want to save your changes?"),
                                   QMessageBox.Save | QMessageBox.Discard
                                   | QMessageBox.Cancel);
        if ret == QMessageBox.Save:
            return self.fileSave();
        elif ret == QMessageBox.Cancel:
            return False;
        return True;

    def fileNew(self):

        if self.maybeSave():
            self.editView.setHtml("<p></p>");
            self.editView.setFocus();
            self.editView.page().setContentEditable(False);
            self.setCurrentFileName(QString());
            self.setWindowModified(False);
    
            # quirk in QeditView: need an initial mouse click to show the cursor
            mx = self.editView.width() / 2;
            my = self.editView.height() / 2;
            center = QPoint(mx, my);
            e1 = QMouseEvent(QEvent.MouseButtonPress, center,
                                              Qt.LeftButton, Qt.LeftButton,
                                              Qt.NoModifier);
            e2 = QMouseEvent(QEvent.MouseButtonRelease, center,
                                              Qt.LeftButton, Qt.LeftButton,
                                              Qt.NoModifier);
            QApplication.postEvent(self.editView, e1);
            QApplication.postEvent(self.editView, e2);

    def fileOpen(self):
            fn = QFileDialog.getOpenFileName(self, self.tr("Open File..."),
                 QString(), self.tr("HTML-Files (*.htm *.html);;All Files (*)"));
            if not fn.isEmpty():
                self.load(fn);


    def fileSave(self):
        if not fileName or fileName.startsWith(QLatin1String(":/")):
                return self.fileSaveAs();

        fileobj = QFile(fileName);
        success = fileobj.open(QIODevice.WriteOnly);
        if success:
            # FIXME: here we always use UTF-8 encoding
            content = self.editView.page().mainFrame().toHtml();
            data = content.toUtf8();
            c = fileobj.write(data);
            success = (c >= data.length());
    
        self.setWindowModified(False);
        return success;


    def fileSaveAs(self):

        fn = QFileDialog.getSaveFileName(self, self.tr("Save as..."),
                     QString(), self.tr("HTML-Files (*.htm *.html);;All Files (*)"));
        if fn.isEmpty():
            return False;
        if not (fn.endsWith(".htm", Qt.CaseInsensitive) or fn.endsWith(".html", Qt.CaseInsensitive)):
            fn += ".htm"; # default
        self.setCurrentFileName(fn);
        return self.fileSave();


# shamelessly copied from Qt Demo Browser
    def guessUrlFromString(self,  urlStr):

        urlStr = urlStr.strip();
        test = QRegExp(QLatin1String("^[a-zA-Z]+\\:.*"));
    
        # Check if it looks like a qualified URL. Try parsing it and see.
        hasSchema = test.exactMatch(urlStr);
        if hasSchema: 
            url = QUrl(urlStr, QUrl.TolerantMode)
            if url.isValid():
                return url;
    

        # Might be a file.
        if QFile.exists(urlStr):
            return QUrl.fromLocalFile(urlStr);
    
        # Might be a shorturl - try to detect the schema.
        if not hasSchema: 
            dotIndex = urlStr.index(QLatin1Char('.'));
            if dotIndex != -1: 
                prefix = urlStr.left(dotIndex).toLower();
                if prefix == QLatin1String("ftp"):
                    schema = prefix
                else:
                    schema = QLatin1String("http");
                url = QUrl(schema + QLatin1String(":#") + urlStr, QUrl.TolerantMode);
                if url.isValid():
                    return url;
            
    
        # Fall back to QUrl's own tolerant parser.
        return QUrl(urlStr, QUrl.TolerantMode);


    def changeZoom(self,  percent):
        self.actionZoomOut.setEnabled(percent > 25);
        self.actionZoomIn.setEnabled(percent < 400);
        factor = float(percent) / 100;
        self.editView.setZoomFactor(factor);

        self.zoomLabel.setText(self.tr(" Zoom: %1% ").arg(percent));
        self.zoomSlider.setValue(percent);

    def closeEvent(self, e):
    
        if self.maybeSave():
            e.accept();
        else:
            e.ignore();

    
    def zoomOut(self):

        percent = int(self.editView.zoomFactor() * 100)
        if percent > 25: 
            percent -= 25;
            percent = 25 * (int((percent + 25 - 1) / 25));
            factor = float(percent) / 100;
            self.editView.setZoomFactor(factor);
            self.actionZoomOut.setEnabled(percent > 25);
            self.actionZoomIn.setEnabled(True);
            self.zoomSlider.setValue(percent);


    def zoomIn(self):

        percent = int(self.editView.zoomFactor() * 100);
        if percent < 400: 
            percent += 25;
            percent = 25 * (int(percent / 25));
            factor = float(percent) / 100;
            self.editView.setZoomFactor(factor);
            self.actionZoomIn.setEnabled(percent < 400);
            self.actionZoomOut.setEnabled(True);
            self.zoomSlider.setValue(percent);
    
    def getEditData(self):
        frame = self.editView.page().mainFrame();
        
        cmd = "editor = CKEDITOR.instances.editor1;editor.getData();"
        return str(frame.evaluateJavaScript(cmd).toString());
        
    def setEditData(self,  data):
        frame = self.editView.page().mainFrame();
        cmd = 'editor = CKEDITOR.instances.editor1;editor.setData(%s);' %repr(data)
        return frame.evaluateJavaScript(cmd).toString()
        
        
    def getCodeData(self):
        frame = self.codeView.page().mainFrame();
        cmd = "editor.mirror.getCode();"
        return str(frame.evaluateJavaScript(cmd).toString());
        
    def setCodeData(self,  data):
        frame = self.codeView.page().mainFrame();
        
        cmd = 'editor.mirror.setCode(%s);' %repr(data)  
        return frame.evaluateJavaScript(cmd).toString();
        
    def execCommand(self, cmd,  arg='null'):

        frame = self.editView.page().mainFrame();
        js = QString("document.execCommand(\"%1\", false, \"%2\")").arg(cmd).arg(arg);
        result = frame.evaluateJavaScript(js)
        log.info("Javascript Execution Result: code: '%s', result type: '%s', result: '%s'" %(js,  result.typeName(),  result.toString()));

    def queryCommandState(self, cmd):

        frame = self.editView.page().mainFrame();
        js = QString("document.queryCommandState(\"%1\", false, null)").arg(cmd);
        result = frame.evaluateJavaScript(js);
        return result.toString().simplified().toLower() == "True";


#define FOLLOW_ENABLE(a1, a2) a1.setEnabled(self.editView.pageAction(a2).isEnabled())
#define FOLLOW_CHECK(a1, a2) a1.setChecked(self.editView.pageAction(a2).isChecked())
    def adjustSource(self):
        self.setWindowModified(True);
        self.sourceDirty = True;

        if self.tabWidget.currentIndex() == 1:
            self.changeTab(1);

    def changeTab(self, index):

        if self.sourceDirty and (index == 1): 
            content = self.editView.page().mainFrame().toHtml();
            #self.plainTextEdit.setPlainText(content);
            self.sourceDirty = False;

    def openLink(self, url):
        msg = QString(self.tr("Open %1 ?")).arg(url.toString());
        if QMessageBox.question(self, self.tr("Open link:"), msg,
                QMessageBox.Open | QMessageBox.Cancel) == QMessageBox.Open:
            QDesktopServices.openUrl(url);


    

    def load(self, f):

        if not QFile.exists(f):
            return False;
        fileobj = QFile(f);
        if not fileobj.open(QFile.ReadOnly):
            return False;
    
        data = fileobj.readAll();
        self.editView.setContent(data, "text/html");
        self.editView.page().setContentEditable(False);
        self.editView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks);
        connect(self.editView, SIGNAL("linkClicked(QUrl)"), self.openLink);
    
        self.setCurrentFileName(f);
        return True;


    def setCurrentFileName(self, fileName):
    
        self.fileName = fileName;
        if not fileName:
            shownName = "untitled";
        else:
            shownName = QFileInfo(fileName).fileName();
    
        self.setWindowTitle(self.tr("%1[*] - %2").arg(shownName).arg(self.tr(self.windowTitle)));
        self.setWindowModified(False);
    
        allowSave = True;
        if not fileName or fileName.startswith(":/"):
            allowSave = False;
        self.actionFileSave.setEnabled(allowSave);

def determine_path ():
    """Borrowed from wxglade.py"""
    try:
        root = __file__
        if os.path.islink (root):
            root = os.path.realpath (root)
        return os.path.dirname (os.path.abspath (root))
    except:
        print "I'm sorry, but something is wrong."
        print "There is no __file__ variable. Please contact the author."
        sys.exit ()

def main():
    os.chdir(determine_path())
    app = QtGui.QApplication(sys.argv)
    for fontfile in glob(os.path.join(determine_path(), 'qt_resources', 'fonts', '*', '*.ttf')):
        QFontDatabase.addApplicationFont(fontfile);
    #QFontDatabase.addApplicationFont( "qt_resources/fonts/cardo/Cardo104s.ttf");
    #QFontDatabase.addApplicationFont( "qt_resources/fonts/cardo/Cardob101.ttf");
    #QFontDatabase.addApplicationFont( "qt_resources/fonts/cardo/Cardoi99.ttf");
    ## Look and feel changed to CleanLooks
    #QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Cleanlooks"))
    #font = QtGui.QFont("Cardo")
    font = QtGui.QFont('Mukthi Narrow', 10)
    font = QtGui.QFont('Bienetresocial', 10)
    app.setFont(font)
    QtGui.QApplication.setPalette(QtGui.QApplication.style().standardPalette())

    window = Rubrique()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
