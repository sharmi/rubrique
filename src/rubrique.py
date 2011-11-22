#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
from urlparse import urlunsplit
from glob import glob 
from PyQt4 import QtGui, QtCore
from ui.rubrique_ui import Ui_MainWindow
from PyQt4.QtCore import QObject,  Qt, QCoreApplication, QEvent, QFile, QFileInfo, QIODevice, QLatin1Char, QLatin1String, QPoint, QRegExp, QString, QStringList, QTimer, QUrl
from PyQt4.QtGui import QWidget,  QComboBox, QSizePolicy,  QIcon,  QLabel,  QSlider, QApplication, QColorDialog, QDesktopServices, QDialog, QFileDialog, QFontDatabase, QInputDialog, QMainWindow, QMessageBox, QMouseEvent, QStyleFactory, QTreeWidgetItem, QWhatsThis, QStandardItemModel, QStandardItem, QListWidgetItem, QAction
from PyQt4.QtWebKit import QWebPage, QWebView, QWebSettings
from core.blogmanager import getBlogManager, RubriqueBlogCommError, RubriqueBlogSetupError
import calendar
from xml.sax.saxutils import quoteattr
from PyQt4.Qsci import QsciScintilla, QsciScintillaBase, QsciLexerHTML, QsciDocument
from editfeature import EditFeature
from edittable import EditTable
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


def showErrorMessage(msg):
    title = "An Error has occurred"
    message = "An error was encountered.  The message is as follows.\n" + msg
    QMessageBox.information(self, title, message, QMessageBox.Ok, QMessageBox.Ok) 

#self.tr = QObject.self.tr
def alert(msg):
    msgbox = QMessageBox('debugmsg', msg)
    msgbox.exec_()

class QPostItem(QListWidgetItem):
    def __init__(self, *args, **kwargs):
        QStandardItem.__init__(self, *args, **kwargs)
        self.post = None


class Rubrique(QtGui.QMainWindow, Ui_MainWindow, EditFeature, EditTable):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
    
        self.fileName = '';
        self.windowTitle = 'Rubrique';
        self.sourceDirty = True;
        highlighter = None;
        ui_dialog = None;
        insertHtmlDialog = None;

        # Setup the ui.
        self.setupUi(self)
        connect(self.tabWidget, SIGNAL("currentChanged(int)"), self.changeTab);
        self.resize(600, 600);
        self.blogs = {}
        self.fontComboBox = QtGui.QFontComboBox()
        self.toolBar.insertWidget(self.actionBold, self.fontComboBox)
        self.sizeComboBox = QtGui.QComboBox()
        self.toolBar.insertWidget(self.actionBold, self.sizeComboBox)

        self.keyLocalPostItemMap = {}
        self.editor = 0;
        self.historyFlag = False;
        
        self.editView.setFocus();
    
        codedir = determine_path()
        self.adjustSource()
        self.setupBlogData();
        self.setWindowModified(False)
        self.autosaveTimer = QTimer(self)
        self.localpostsList.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.actionLocalPostOpen = QAction("Open", self.localpostsList)
        self.actionLocalPostDelete = QAction("Delete", self.localpostsList)
        self.localpostsList.addAction(self.actionLocalPostOpen)
        self.localpostsList.addAction(self.actionLocalPostDelete)
        self.setupCodeView()
        self.setupTriggers()

    def setupCodeView(self):
        ## set the default font of the self.codeView
        ## and take the same font for line numbers
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setFixedPitch(True)
        font.setPointSize(10)         
        fm = QtGui.QFontMetrics(font)

        self.codeView.setFont(font)
        self.codeView.setMarginsFont(font)

        ## Line numbers
        # conventionnaly, margin 0 is for line numbers
        self.codeView.setMarginWidth(0, fm.width( "00000" ) + 5)
        self.codeView.setMarginLineNumbers(0, True)

        ## Edge Mode shows a red vetical bar at 80 chars
        #self.codeView.setEdgeMode(QsciScintilla.EdgeLine)
        #self.codeView.setEdgeColumn(80)
        #self.codeView.setEdgeColor(QtGui.QColor("#FF0000"))

        self.codeView.setWrapMode(QsciScintilla.WrapWord)
        ## Folding visual : we will use boxes
        self.codeView.setFolding(QsciScintilla.BoxedTreeFoldStyle)

        ## Braces matching
        self.codeView.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        ## Editing line color
        self.codeView.setCaretLineVisible(True)
        self.codeView.setCaretLineBackgroundColor(QtGui.QColor("#CDA869"))

        ## Margins colors
        # line numbers margin
        self.codeView.setMarginsBackgroundColor(QtGui.QColor("#333333"))
        self.codeView.setMarginsForegroundColor(QtGui.QColor("#CCCCCC"))

        # folding margin colors (foreground,background)
        self.codeView.setFoldMarginColors(QtGui.QColor("#99CC66"),QtGui.QColor("#333300"))
        #self.editView.setHtml(open('textedit/example.html').read())
        self.testView.setDocument(self.editView.document())
        #highlighter = XMLHighlighter(self.testView.document())

        ## Choose a lexer
        lexer = QsciLexerHTML()
        lexer.setDefaultFont(font)
        self.codeView.setLexer(lexer)
        self.codeView.setText(self.editView.toHtml())

    def setupTriggers(self):
        connect(self.autosaveTimer, SIGNAL("timeout()"), self.saveBlogContent)
        #self.autosaveTimer.start(2000)
        connect(self.actionPublish,  SIGNAL("triggered()"), self.publish)
        connect(self.actionFileNew, SIGNAL("triggered()"), self.fileNew);
        connect(self.actionFileSave, SIGNAL("triggered()"), self.saveBlogContent);
        connect(self.actionExit, SIGNAL("triggered()"), self.close);
        connect(self.actionAddNewBlog, SIGNAL("triggered()"), self.addNewBlogDialog)     
        connect(self.postTitleTxt, SIGNAL("textEdited(QString)"), self.titleChanged) 
        connect(self.excerptTxt, SIGNAL("textChanged()"), self.setExcerpt)
        connect(self.trackbacksCheck, SIGNAL("stateChanged(int)"), self.blogManager.allowTrackbacks)
        connect(self.commentsCheck, SIGNAL("stateChanged(int)"), self.blogManager.allowComments)
        connect(self.localpostsList, SIGNAL("itemActivated(QListWidgetItem *)"), self.loadLocalPost)
        connect(self.actionLocalPostOpen, SIGNAL("triggered()"), self.loadLocalPost)
        connect(self.actionLocalPostDelete, SIGNAL("triggered()"), self.deleteLocalPost)
        connect(self.categoriestree, SIGNAL("itemChanged (QTreeWidgetItem *,int)"), self.changeCategories)

        self.connect(self.blogCombo,
                     SIGNAL("currentIndexChanged(int)"),
                     self.currentBlogChanged)
        self.connect(self.postBlogCombo,
                     SIGNAL("currentIndexChanged(int)"),
                     self.currentPostBlogChanged)
        self.connect(self.postTree, 
                     SIGNAL("itemActivated(QTreeWidgetItem * , int)"), self.loadOnlinePost)
        connect(self.actionBold, SIGNAL("triggered()"), self.textBold)
        connect(self.actionTable, SIGNAL("triggered()"), self.insertTable)
        connect(self.actionItalics, SIGNAL("triggered()"), self.textItalic)
        connect(self.actionUnderline, SIGNAL("triggered()"), self.textUnderline)
        connect(self.actionBeforeRow, SIGNAL("triggered()"), self.insertRowsBefore)
        connect(self.actionAfterRow, SIGNAL("triggered()"), self.insertRowsAfter)
        connect(self.actionBeforeColumn, SIGNAL("triggered()"), self.insertColumnsBefore)
        connect(self.actionAfterColumn, SIGNAL("triggered()"), self.insertColumnsAfter)
        connect(self.actionDelete_Rows, SIGNAL("triggered()"), self.deleteRows)
        connect(self.actionDelete_Columns, SIGNAL("triggered()"), self.deleteColumns)
        connect(self.actionMerge_Selected_Cells, SIGNAL("triggered()"), self.mergeCells)
        connect(self.actionSplit_Cell, SIGNAL("triggered()"), self.splitCell)
        connect(self.actionUndo, SIGNAL("triggered()"), self.undo)
        connect(self.actionRedo, SIGNAL("triggered()"), self.redo)
        connect(self.codeView, SIGNAL("textChanged()"), self.syncHistory)
        connect(self.editView, SIGNAL("textChanged()"), self.syncHistory)


    def blogManagerErrorHandler(f):
        def errorfunc(*args):
            try:
                return f(*args)
            except RubriqueBlogCommError, e:
                showErrorMessage(str(e))
        return errorfunc

    def changeCategories(self, item, column):
        catname = unicode(item.text(0))
        if item.checkState(0) == Qt.Checked:
            self.blogManager.addCategory(catname)
        else:
            self.blogManager.removeCategory(catname)

    def loadOnlinePost(self, postitem, column):
        self.autosaveTimer.stop()
        postid = int(postitem.data(0, Qt.UserRole).toInt()[0])
        rubriqueKey = str(self.blogCombo.itemData(self.blogCombo.currentIndex()).toString())
        self.saveBlogContent()
        self.blogManager.loadOnlinePost (rubriqueKey, postid)
        self.initUIData()
        #self.autosaveTimer.start(5000)



    @blogManagerErrorHandler
    def currentBlogChanged(self, index):
        self.postTree.clear()
        self.populatePosts()
        pass

    @blogManagerErrorHandler
    def currentPostBlogChanged(self, index):
        self.categoriestree.clear()
        rubriqueKey = str(self.postBlogCombo.itemData(index).toString())
        self.blogManager.setCurrentBlog(rubriqueKey)
        self.populateCategories()
        self.checkPostCategories()
        pass

    def setExcerpt(self):
        self.blogManager.setExcerpt(unicode(self.excerptTxt.toPlainText()))

    def loadLocalPost(self, postitem=None):
        self.saveBlogContent()
        if postitem == None:
            postitem = self.localpostsList.currentItem() 
        self.blogManager.setCurrentPost(postitem.post)
        self.initUIData()

    def deleteLocalPost(self):
        postitem = self.localpostsList.currentItem() 
        if postitem.post is self.blogManager.currentPost:
            self.fileNew()
        self.blogManager.deleteLocalPost(postitem.post)
        self.localpostsList.takeItem(self.localpostsList.currentRow())
        del postitem


    def titleChanged(self, title):
        title = unicode(title)
        self.blogManager.setTitle(title)
        self.setWindowTitle(self.tr("%1[*] - %2").arg(title).arg(self.tr(self.windowTitle)));
        self.keyLocalPostItemMap[self.blogManager.currentPost.id].setText(title)
        #self.setWindowModified(False);
        #TODO also change in localpostsList

    def setLocalPostsList(self):
        #model = QStandardItemModel()
        #count = 0
        for post in self.blogManager.localposts.query.all():
            postitem = QPostItem(str(post))
            postitem.post = post
            self.localpostsList.addItem(postitem)
            self.keyLocalPostItemMap[post.id] = postitem
            #count =+ 1
        #self.localpostsList.setModel(model)
    
    def checkPostCategories(self):
        categories = self.blogManager.currentPost.categories
        for catitem in self.catItemsMap.values():
            catitem.setCheckState(0, Qt.Unchecked)
        for catname in categories:
            self.catItemsMap[catname].setCheckState(0, Qt.Checked)

    def initUIData(self):
        print self.blogManager.currentPost.categories
        title = self.blogManager.getTitle()
        print self.windowTitle, "$", title
        self.setWindowTitle(self.tr("%1[*] - %2").arg(title).arg(self.tr(self.windowTitle)));
        self.postTitleTxt.setText(title)
        self.excerptTxt.setPlainText(self.blogManager.getExcerpt())
        self.checkPostCategories()
        self.trackbacksCheck.setChecked(self.blogManager.allowTrackbacks())
        self.commentsCheck.setChecked(self.blogManager.allowComments())
        self.setLocalPostsList()
        self.reloadFlag = True
        #self.codeView.reload()
        #self.editView.reload()


    def loadPostContent(self, flag):
        if not self.reloadFlag:
            return
        self.reloadFlag = False
        print "called", self.reloadFlag
        self.autosaveTimer.stop()
        postBody = self.blogManager.getPostBody()
        self.setEditData(postBody)
        self.setCodeData(postBody)
        self.preView.setHtml(postBody)
        #self.autosaveTimer.start(2000)
        
    def syncHistory(self):
        #0 -> EditView 1->CodeView 2->Preview
        if self.historyFlag == True:
            self.historyFlag = False
            return
        currentIndex =  self.tabWidget.currentIndex()
        self.historyFlag = True
        latestData = ''
        if currentIndex == 0:
            latestData = self.editView.toHtml()
            self.codeView.setText(latestData)
        elif currentIndex == 1:
            latestData = self.codeView.text()
            cursor = self.editView.textCursor()
            cursor.select(QtGui.QTextCursor.Document)
            cursor.insertHtml(latestData)
            #self.editView.setHtml(latestData)
            
        self.preView.setHtml(latestData)
     
    def undo(self):
        self.editView.document().undo()
        self.dataFromHistory()

    def redo(self):
        self.editView.document().redo()
        self.dataFromHistory()

    def dataFromHistory(self):
        data = self.editView.toHtml()
        #self.editView.setHtml(data)
        self.codeView.setText(data)
        self.preView.setHtml(data)

    def syncEditors(self,  force=False):
        return True
        #0 -> EditView 1->CodeView 2->Preview
        currentIndex =  self.tabWidget.currentIndex()
        if currentIndex!= self.editor or force==True:
            if self.editor == 0 :
                latestData = self.editView.toHtml()
                self.codeView.setText(latestData)
                #Set Preview data
            elif self.editor == 1:
                latestData = self.codeView.text()
                self.editView.setHtml(latestData)
            self.preView.setHtml(latestData)
            if currentIndex in [0,  1]:
               self.editor  = currentIndex
        return True
        
    def populateBlogCombos(self, blog=None):
        if blog:
            #self.comboSelector.addItem("%s: %s" %(blog.blogname, blog.username))
            log.info('Adding new blog %s to both combos' %blog.rubriqueKey)
            self.blogCombo.addItem("%s: %s" %(blog.blogname, blog.username), blog.rubriqueKey)
            self.postBlogCombo.addItem("%s: %s" %(blog.blogname, blog.username), blog.rubriqueKey)
            
            return
        for rubriqueKey in self.blogManager.serviceApis:
            #blog = self.blogManager.blogs[rubrique_key]
            blog = self.blogManager.getBlogByKey(rubriqueKey)
            self.blogCombo.addItem("%s: %s" %(blog.blogname, blog.username), blog.rubriqueKey)
            self.postBlogCombo.addItem("%s: %s" %(blog.blogname, blog.username), blog.rubriqueKey)
        for rubriqueKey, (api, msg) in self.blogManager.failedServiceApis.iteritems():
            blog = self.blogManager.getBlogByKey(rubriqueKey)
            self.blogCombo.addItem("%s: %s" %(blog.blogname, blog.username), blog.rubriqueKey)
            index = self.blogCombo.findData(rubriqueKey)
            model = self.blogCombo.model()
            item = model.item(index)
            item.setSelectable(False)
            item.setEnabled(False)
            item.setToolTip(msg)
            pass
        if self.blogManager.currentBlog:
            rubriqueKey = self.blogManager.currentBlog.rubriqueKey
            index = self.blogCombo.findData(rubriqueKey)
            self.blogCombo.setCurrentIndex(index)
            index = self.postBlogCombo.findData(rubriqueKey)
            self.postBlogCombo.setCurrentIndex(index)
        else:
            index = -1
            self.blogCombo.setCurrentIndex(index)
        return
    
    def addNewBlog(self, blog):
        addedBlog = self.blogManager.addBlog(blog)
        if addedBlog is None:
            title = "Added Blog is Duplicate"
            message = "The Blog that you are trying to add already exists in our database."
            QMessageBox.information(self, title, message, QMessageBox.Ok, QMessageBox.Ok) 
            return
        self.populateBlogCombos(addedBlog)
        index = self.blogCombo.findData(addedBlog.rubriqueKey)
        self.blogCombo.setCurrentIndex(index)
        #self.blogManager.setCurrentBlog(blog.rubriqueKey)
        title = "Added New Blog: %s"% blog.blogname 
        message = "The blog with the following details have been added to the repository.\n Blog Name: %s\nUsername: %s\nUrl: %s\nBlog Engine: %s" %(blog.blogname, blog.username, blog.homeurl, blog.apis[blog.preferred]['name']) 
        QMessageBox.information(self, title, message, QMessageBox.Ok, QMessageBox.Ok) 

    def addNewBlogDialog(self):
        newblog = addblogdialog.addNewBlog(self.addNewBlog)
        if not newblog: return
        #self.blogManager.set_current_blog(newblog.rubrique_key)
        
    def donothing(self):
        pass
    def setupBlogData(self):
        self.blogManager = getBlogManager()
        #self.blogManager.loadConnections()
        self.populateBlogCombos()
        self.populatePosts()
        self.blogManager.refreshCategories(allBlogs=True)
        self.populateCategories()
        self.initUIData()
        #self.blogManager.add_blog('wordpress', 'http://www.minvolai.com/blog/xmlrpc.php', 'sharmila', 'letmein')

    def _addChildren(self, parent, parentitem, parent_child_dict):
        print "In"
        if parent.catId not in parent_child_dict:
            print parent.catId
            return
        for child in parent_child_dict[parent.catId]:
            catitem = QTreeWidgetItem(parentitem)
            self.catItemsMap[child.name] = catitem
            self._addChildren(child, catitem, parent_child_dict)
            catitem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled)
            #catitem.setIcon(0, blueico)
            catitem.setText(0, child.name)
            catitem.setToolTip(0, child.description)
        
    def populateCategories(self):
        categories = self.blogManager.getCategories()
        self.catItemsMap = {}
        if not categories:
            self.categoriestree.clear()
            return
        self.categoriestree.setColumnCount(1)
        parent_child_dict = {}
        for cat in categories:
            if cat.parentId not in parent_child_dict:
                parent_child_dict[cat.parentId] = []
            parent_child_dict[cat.parentId].append(cat)
        print parent_child_dict
        for child in parent_child_dict[0]:
            catitem = QTreeWidgetItem(self.categoriestree)
            self.catItemsMap[child.name] = catitem
            self._addChildren(child, catitem, parent_child_dict)

            #catitem.setIcon(0, blueico)
            catitem.setText(0, child.name)
            catitem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled)
            catitem.setToolTip(0, child.description)

    def populatePosts(self):
        print self.blogCombo.currentIndex()
        rubriqueKey = str(self.blogCombo.itemData(self.blogCombo.currentIndex()).toString())
        print 'rubriquekey', rubriqueKey
        posts = self.blogManager.getLatestPosts(rubriqueKey=rubriqueKey)
        if not posts:
            self.postTree.clear()
            return
        yeardict = {}
        year_month = {}
        self.postTree.setColumnCount(1)
        blueico = QIcon("images/turquoise_button.png")
        postico = QIcon("images/open_local_post.png")
        for post in posts:
            year, month = post.date.year, post.date.month
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
            postobj.setData(0, Qt.UserRole, post.postid)
            postobj.setToolTip(0, post.title)
             

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
        self.saveBlogContent()
        self.blogManager.setCurrentPost()
        self.initUIData()
    
    
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

    def closeEvent(self, e):
    
        if self.maybeSave():
            e.accept();
        else:
            e.ignore();

#define FOLLOW_ENABLE(a1, a2) a1.setEnabled(self.editView.pageAction(a2).isEnabled())
#define FOLLOW_CHECK(a1, a2) a1.setChecked(self.editView.pageAction(a2).isChecked())
    def adjustSource(self):
        self.setWindowModified(True);
        self.sourceDirty = True;

        if self.tabWidget.currentIndex() == 1:
            self.changeTab(1);

    def changeTab(self, index):

        if self.sourceDirty and (index == 1): 
            content = self.editView.toHtml();
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
    #font = QtGui.QFont('Bienetresocial', 10)
    #app.setFont(font)
    QtGui.QApplication.setPalette(QtGui.QApplication.style().standardPalette())

    window = Rubrique()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
