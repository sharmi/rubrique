import platform
import xmlrpclib
import os
import sys
import logging
import pod
import socket
import datetime
from elixir import *
from core.bloginterfaces.blog import RubriqueBlogAccount, LocalPost, Category, OnlinePost, RubriqueBlogAccountDB, CategoryRec, AppStatus, generateRubriqueKey
import core.bloginterfaces.adapter as adapter
import rsd
from core.bloginterfaces.metaweblog import MetaWeblogException
METAWEBLOG = 'metaweblog'
WORDPRESS = 'wordpress'
log = logging.getLogger("rubrique")
class RubriqueBlogSetupError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class RubriqueBlogCommError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class UnknownPlatform(Exception):
    def __init__(self, platform):
        self.msg = "'%s' platform is not supported." %(platform)

    def __str__(self):
        return repr(self.msg)

class BlogManager(object):
    myAppDataFolder = "rubrique"
    def __init__(self):
        self.__setupDataPath()
        self.blogs = RubriqueBlogAccountDB
        self.serviceApis = {}
        self.failedServiceApis = {}
        self.posts = {}  #
        self.localposts = LocalPost
        self.categories = Category
        self.currentApi = None
        self.loadConnections()
        self.appStatus = AppStatus.query.first()
        if self.appStatus is None:
            self.appStatus = AppStatus()
        if self.appStatus.currentBlog and self.appStatus.currentBlog.rubriqueKey in self.serviceApis:
            print "currentBlog is", self.appStatus.currentBlog
            self.setCurrentBlog(self.appStatus.currentBlog.rubriqueKey)
        else:
            self.currentBlog = None
        if self.appStatus.currentPost:
            self.currentPost = self.appStatus.currentPost
        else:
            self.setCurrentPost()
        log.info("Current Post")
        log.info(self.currentPost)
        session.commit()

    def allKeys(self):
        return [x.rubriqueKey for x in self.blogs.query.all()]

    def dbCommit(f):
        def funcDBCommit(*args, **kwargs):
            returnVal = f(*args, **kwargs)
            session.commit()
            return returnVal
        funcDBCommit.__name__ = f.__name__
        return funcDBCommit

    def errorHandler(f):
        def errorfunc(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except socket.gaierror, e:
                log.exception(e)
                raise RubriqueBlogCommError("Unable to communicate with blog engine : Error received %s" %str(e))
            #except xmlrpclib.ProtocolError, e:
            #    log.exception(e)
            #    raise RubriqueBlogCommError("Unable to communicate with blog engine : Error received %s" %str(e))
        return errorfunc
        
    def __setupDataPath(self):
        if platform.system() == "Linux":
            self.datapath = os.path.join(os.path.expanduser("~") , ".local" , "share",  self.myAppDataFolder)
        elif platform.system() == "Windows":
#Windows code:
            self.datapath = os.path.join(os.getenv("APPDATA"), self.myAppDataFolder)
        else:
            raise UnknownPlatform(platform.system())
            sys.exit(1)
        if not os.path.exists(self.datapath):
            os.makedirs(self.datapath, 0744)
        self.dbpath = os.path.join(self.datapath, "rubrique.db")

    @dbCommit
    def deleteLocalPost(self, localpost):
        localpost.delete()


        
    def getBlogs(self, url, username, password, blogId = None):
        try:
            blogService, homeurl, apis, preferred = rsd.get_rsd(url)
        except rsd.RSDError, e:
            raise RubriqueBlogSetupError("Failed to resolve blogtype. Manual entry required. Error Message as follows '%s'" %e)
            return -1
        apiurl = apis[preferred]['apiLink']
        blogtype = preferred
        blogid = apis[preferred]['blogID']
        resolvedBlogtype = self._resolve(blogtype)
        serviceApi = self._serviceApiFactory(resolvedBlogtype, apiurl, username, password)
        blogs =  serviceApi.getBlogs()
        for tblog in blogs:
            log.info("Detected Blog " + str(tblog))
        if not blogs:
            raise RubriqueBlogSetupError("Api is Unaware of any blogs")
        blogaccs = []
        for blog in blogs:
            blogaccs.append(RubriqueBlogAccount(blog.id, blog.name, username, password, blog.url, apiurl, apis, preferred, resolvedBlogtype))
        return blogaccs

    def _resolve(self, blogtype):
        if blogtype in [METAWEBLOG, WORDPRESS]: 
            return METAWEBLOG
        else:
            raise RubriqueBlogSetupError("BlogType " + blogtype + " is not supported")

    def _serviceApiFactory(self, blogtype, apiurl, username, password):
        if blogtype  == METAWEBLOG: 
            return adapter.MetaWeblogAdapter(apiurl, username, password)
        else:
            raise RubriqueBlogSetupError("BlogType " + blogtype + " needs to be resolved")

    def _serviceApiForAcc(self, blogacc):
        return self._serviceApiFactory(blogacc.resolved, blogacc.apiurl, blogacc.username, blogacc.password)

    @dbCommit
    def addBlog(self, blogacc):
        if blogacc:
            rubriqueKey = generateRubriqueKey(blogacc.blogname, blogacc.username)
            if self.getBlogByKey(rubriqueKey):
                return None
            blogaccrec = RubriqueBlogAccountDB()
            self.initBlogAccRec(blogaccrec, blogacc)
        return blogacc


    def initBlogAccRec(self, rec, obj):
        rec.blogid = obj.blogid
        rec.blogname = obj.blogname.strip()
        rec.username = obj.username.strip()
        rec.password = obj.password
        rec.homeurl = obj.homeurl
        rec.apiurl = obj.apiurl
        rec.apis = obj.apis
        rec.preferred = obj.preferred
        rec.resolved = obj.resolved
        rec.rubriqueKey = generateRubriqueKey(rec.blogname, rec.username)

    @dbCommit
    def setCurrentPost(self, post=None):
        if post is None:
            self.currentPost = LocalPost()
        else:
            self.currentPost = post
        self.appStatus.currentPost = self.currentPost

    @dbCommit
    def addCategory(self, catId):
        if catId not in self.currentPost.categories:
            self.currentPost.categories.append(catId)

    @dbCommit
    def removeCategory(self, catId):
        if catId in self.currentPost.categories:
            self.currentPost.categories.remove(catId)

        

    @dbCommit
    def loadOnlinePost(self, rubriqueKey, postid):
        post = self.serviceApis[rubriqueKey].getPost(postid)
        self.setCurrentPost()
        self.loadInCurrent(post)
        self.setCurrentBlog(rubriqueKey)

    def loadInCurrent(self, post):
        self.currentPost.title = post.title
        self.currentPost.postid = post.postid
        self.currentPost.date = post.date
        self.currentPost.permaLink = post.permaLink
        self.currentPost.description = post.description
        self.currentPost.textMore = post.textMore
        self.currentPost.excerpt = post.excerpt
        self.currentPost.link = post.link
        self.currentPost.categories = post.categories
        self.currentPost.tags = post.tags
        self.currentPost.user = post.user
        self.currentPost.allowPings = post.allowPings
        self.currentPost.allowComments = post.allowComments
        self.currentPost.status = post.status

    def getBlogByKey(self, key):
        return self.blogs.get_by(rubriqueKey=key)

    def loadConnections(self):
        for blog in self.blogs.query.all():
            api = self._serviceApiForAcc(blog)
            try:
                api.ping()
                self.serviceApis[blog.rubriqueKey] = api
                print blog.rubriqueKey, 'passed'
            except (xmlrpclib.ProtocolError, socket.gaierror, xmlrpclib.Fault, MetaWeblogException, socket.error), e:
                print blog.rubriqueKey, 'failed'
                log.warning(e)
                self.failedServiceApis[blog.rubriqueKey] = (api, str(e))
                

    @dbCommit
    def setCurrentBlog(self, rubriqueKey):
        self.currentBlog = self.getBlogByKey(rubriqueKey)
        self.appStatus.currentBlog = self.currentBlog
        if rubriqueKey not in self.serviceApis:
            self.serviceApis[rubriqueKey] = self._serviceApiForAcc(self.currentBlog)
        self.currentApi = self.serviceApis[rubriqueKey]
        print "setup blog successfully"

    @errorHandler
    def getLatestPosts(self, num=10, rubriqueKey=None, allBlogs=None):
        if rubriqueKey is None or rubriqueKey == '':
            return []
        #rubriqueKey = blog.rubriqueKey
        blog = self.getBlogByKey(rubriqueKey)
        if rubriqueKey in self.posts:
            return self.posts[rubriqueKey]
        #if rubriqueKey not in self.serviceApis:
        #    self.serviceApis[rubriqueKey] = self._serviceApiForAcc(blog)
        latestPosts = self.serviceApis[rubriqueKey].getPosts(num)
        self.posts[rubriqueKey] = latestPosts
        return latestPosts
    
    @errorHandler
    @dbCommit
    def getCategories(self):
        if self.currentBlog:
            categories = CategoryRec.query.filter_by(blog=self.currentBlog).all()
            if not categories:
                self.refreshCategories()
            categories = CategoryRec.query.filter_by(blog=self.currentBlog).all()
            return categories
        else:
            return []

    @dbCommit
    def refreshCategories(self, rubriqueKey=None, allBlogs=False):
        if allBlogs:
            for key in self.serviceApis:
                self.refreshCategories(rubriqueKey=key)
            return
        if rubriqueKey == '':
            return []
        if rubriqueKey is None:
            if self.currentBlog:
                blog = self.currentBlog
                rubriqueKey = self.currentBlog.rubriqueKey
            else:
                return []
        else:
            blog = self.getBlogByKey(rubriqueKey)
        
        existing_categories = CategoryRec.query.filter_by(blog=blog)
        categories = self.serviceApis[rubriqueKey].getCategories()
        if not categories: return
        existing_catids = [item.catId for item in existing_categories]
        obtained_catids = [item.catId for item in categories]
        catids_to_remove = set(existing_catids) - set(obtained_catids)
        catids_to_update = set(existing_catids).intersection(set(obtained_catids))
        new_catids = set(obtained_catids) - set(existing_catids)
        for catId in catids_to_remove:
            for rec in categories:
                if rec.catId == catId:
                    rec.delete()

        for catId in catids_to_remove:
            for rec in categories:
                if rec.catId == catId:
                    for obj in categories:
                        if rec.catId == obj.catId:
                            self.updateCategories(rec, obj)

        for catId in new_catids:
            for obj in categories:
                if obj.catId == catId:
                    rec = CategoryRec()
                    self.updateCategories(rec, obj)
                    rec.blog = blog
            
    def updateCategories(self, rec, obj):
        rec.catId = obj.catId
        rec.name = obj.name
        rec.isPrimary = obj.isPrimary
        rec.parentId = obj.parentId
        rec.description = obj.description
        

    def publish(self):
        if self.currentApi:
            self.currentApi.publishPost(self.currentPost)
        else:
            return None

    @dbCommit
    def setPostBody(self, content):
        self.currentPost.description = content

    def getPostBody(self):
        return self.currentPost.description + self.currentPost.textMore

    @dbCommit
    def setTitle(self, title):
        self.currentPost.title = title

    def getTitle(self):
        return self.currentPost.title

    def getExcerpt(self):
        return self.currentPost.excerpt

    @dbCommit
    def setExcerpt(self, excerpt):
        self.currentPost.excerpt = excerpt

    @dbCommit
    def allowTrackbacks(self, allow=None):
        if allow is None:
            return self.currentPost.allowPings
        if allow:
            self.currentPost.allowPings = True
        else:
            self.currentPost.allowPings = False
    
    @dbCommit
    def allowComments(self, allow=None):
        if allow is None:
            return self.currentPost.allowComments
        if allow:
            self.currentPost.allowComments = True
        else:
            self.currentPost.allowComments = False
    
    
blogManager = BlogManager()
def getBlogManager():
    return blogManager
