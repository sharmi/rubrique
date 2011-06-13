import platform
import os
import sys
import logging
import pod
from core.bloginterfaces.blog import RubriqueBlogAccount, LocalPost, Category, OnlinePost, RubriqueBlogAccountPOD
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
        self.posts = OnlinePost  #
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
        print "here"
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
            RubriqueBlogAccountPOD(blogacc)
            self.db.commit()
        pass

    @dbCommit
    def setCurrentPost(self, post=None):
        if post is None:
            self.currentPost = LocalPost()
        else:
            self.currentPost = post
        self.appStatus.currentPost = self.currentPost

    def getBlogByKey(self, key):
        return (self.blogs.where.rubriqueKey == key).get_one()


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

    def getLatestPosts(self, num=10):
        if self.currentApi:
            return self.currentApi.getPosts(num)
        else:
            return []
        
    def getCategories(self):
        if self.currentApi:
            return self.currentApi.getCategories()
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
        return self.currentPost.description

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
