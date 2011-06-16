import platform
import os
import sys
import logging
import pod
import socket
import datetime
from core.bloginterfaces.blog import RubriqueBlogAccount, LocalPost, Category, OnlinePost, RubriqueBlogAccountPOD, BlogCategories
import core.bloginterfaces.adapter as adapter
import rsd
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
        self.blogs = RubriqueBlogAccountPOD
        self.serviceApis = {}
        self.posts = {}  #
        self.localposts = LocalPost
        self.categories = Category
        self.currentApi = None
        self.appStatus = self.db.store
        try:
            if self.appStatus.currentBlog:
                self.setCurrentBlog(self.appStatus.currentBlog.rubriqueKey)
        except pod.db.PodStoreError:
            self.currentBlog = None
        try:
            self.currentPost = self.appStatus.currentPost
        except pod.db.PodStoreError:
            self.setCurrentPost()
        log.info("Current Post")
        log.info(self.currentPost)
        self.db.commit()

    def dbCommit(f):
        def funcDBCommit(*args):
            returnVal = f(*args)
            args[0].db.commit()
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
        self.db= pod.Db(file=self.dbpath)

    @dbCommit
    def deleteLocalPost(self, localpost):
        del localpost

        
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
            blogacc = RubriqueBlogAccountPOD(blogacc)
        return blogacc

    @dbCommit
    def setCurrentPost(self, post=None):
        if post is None:
            self.currentPost = LocalPost()
        else:
            self.currentPost = post
        self.appStatus.currentPost = self.currentPost

    @dbCommit
    def addCategory(self, catname):
        if catname not in self.currentPost.categories:
            self.currentPost.categories.append(catname)
        print self.currentPost.categories

    @dbCommit
    def removeCategory(self, catname):
        if catname in self.currentPost.categories:
            self.currentPost.categories.remove(catname)
        print self.currentPost.categories

        

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
        for blog in self.blogs.where.rubriqueKey == key:
            return blog
        return None


    def setCurrentBlog(self, rubriqueKey):
        self.currentBlog = self.getBlogByKey(rubriqueKey)
        self.appStatus.currentBlog = self.currentBlog
        if rubriqueKey not in self.serviceApis:
            self.serviceApis[rubriqueKey] = self._serviceApiForAcc(self.currentBlog)
        self.currentApi = self.serviceApis[rubriqueKey]
        self.db.commit()
        #if rubriqueKey not in self.posts:
        #    self.posts[rubriqueKey] = SQLiteShelf(self.dbpath, "posts_"+rubriqueKey)
        #if rubriqueKey not in self.localposts:
        #    self.localposts[rubriqueKey] = SQLiteShelf(self.dbpath, "localposts_"+rubriqueKey)
        #if rubriqueKey not in self.categories:
        #    self.categories[rubriqueKey] = SQLiteShelf(self.dbpath, "categories_"+rubriqueKey)
    @errorHandler
    def getLatestPosts(self, num=10, rubriqueKey=None):
        if rubriqueKey is None:
            return []
        #rubriqueKey = blog.rubriqueKey
        blog = self.getBlogByKey(rubriqueKey)
        if rubriqueKey in self.posts:
            return self.posts[rubriqueKey]
        if rubriqueKey not in self.serviceApis:
            self.serviceApis[rubriqueKey] = self._serviceApiForAcc(blog)
        latestPosts = self.serviceApis[rubriqueKey].getPosts(num)
        self.posts[rubriqueKey] = latestPosts
        return latestPosts
    
    @errorHandler
    @dbCommit
    def getCategories(self):
        if self.currentApi:
            blogcatmap = None
            for blogcatmap in BlogCategories.where.blog == self.currentBlog:
                blogcatmap = blogcatmap
                break
            if blogcatmap:
                if datetime.datetime.utcnow() - blogcatmap.lastqueriedtime > datetime.timedelta(hours=1):
                    try:
                        blogcatmap.categories = self.currentApi.getCategories()
                        blogcatmap.lastqueriedtime = datetime.datetime.utcnow()
                    except e:
                        log.exception("Failed to latest categories for blog" %self.currentBlog)
                return blogcatmap.categories
            else:
                blogcatmap = BlogCategories()
                blogcatmap.blog = self.currentBlog
                try:
                    blogcatmap.categories = self.currentApi.getCategories()
                    blogcatmap.lastqueriedtime = datetime.datetime.utcnow()
                except e:
                    log.exception("Failed to latest categories for blog" %self.currentBlog)
                return blogcatmap.categories
        else:
            return []

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
