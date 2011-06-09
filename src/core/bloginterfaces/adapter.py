from core.bloginterfaces.metaweblog import MetaWeblogClient, MetaWeblogException
import logging
log = logging.getLogger("rubrique")
class Features(object):
    def __init__(self):
        self.posts = True
        self.categories  = False
        self.categoriesAdd = False
        self.pages = False
        self.tags = False

class RubriqueBloggingError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "RubriqueBlogging Error: %s" %self.msg

class Adapter(object):
 
    def __init__(self, url, username, password, blogid=None):
        self.username = username
        self.password = password
        self.url = url
        self.blogid = blogid
        self.features = Features()

    def authenticate(self):
        raise RubriqueBloggingError("Failed To Authenticate. Auth routine not implemented")

    def getPosts(self, count=20):
        pass

    def publishPost(self, post):
        pass

    def publishDraft(self, post):
        pass

    def getCategories(self):
        pass

    def addCategory(self, category):
        pass

    def updatePost(self, post):
        pass

    def getBlogs(self):
        pass

    def uploadMediaObj(self):
        pass

class MetaWeblogAdapter(Adapter):
    def __init__(self, *args):
        Adapter.__init__(self, *args)
        log.info("Creating metaweblog client with url: %s and username: %s"%(self.url, self.username))
        self.client = MetaWeblogClient(self.url, self.username, self.password)

    def handleMWException(f):
        def new_f(*args):
            try:
                return f(*args)
            except MetaWeblogException, e:
                log.error(e)
                raise RubriqueBloggingError(e.message)
        new_f.__name__ = f.__name__
        return new_f



    def authenticate(self):
        pass

    @handleMWException
    def selectBlog(self, blogid):
        return self.client.selectBlog(blogid)

    @handleMWException
    def getPosts(self, count=20):
           return self.client.getRecentPosts(count) 

    @handleMWException
    def publishDraft(self, post):
        self.client.newPost(post, False)

    @handleMWException
    def publishPost(self, post):
        self.client.newPost(post, True)

    @handleMWException
    def getCategories(self):
        return self.client.getCategoryList()

    @handleMWException
    def addCategory(self, category):
        pass

    @handleMWException
    def updatePost(self, post, publish):
        self.client.editPost(post.id, post,  publish) 

    @handleMWException
    def getBlogs(self):
        blogs = [blog for blog in self.client.getUsersBlogs()]
        return blogs

    @handleMWException
    def uploadMediaObj(self, filename=None, fileobj=None):
        self.client.newMediaObject(self, filename, fileobj)


