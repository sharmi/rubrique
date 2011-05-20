from core.bloginterfaces.metaweblog import MetaWeblogClient, MetaWeblogException
import logging
log = logging.getLogger("rubrique")
class Features(object):
    def __init__(self):
        self.posts = True
        self.categories  = False
        self.categories_add = False
        self.pages = False
        self.tags = False

class RubriqueBloggingError(Exception):
    def __init__(self, msg):
        self.msg = msg

class Adapter(object):
 
    def __init__(self, url, username, password, blogid=None):
        self.username = username
        self.password = password
        self.url = url
        self.blogid = blogid
        self.features = Features()

    def authenticate(self):
        raise RubriqueBloggingError("Failed To Authenticate. Auth routine not implemented")

    def get_posts(self, default_count=20):
        pass

    def publish_post(self, post):
        pass

    def publish_draft(self, post):
        pass

    def get_categories(self):
        pass

    def add_category(self, category):
        pass

    def update_post(self, post):
        pass

    def get_blogs(self):
        pass

    def upload_media_obj(self):
        pass

class MetaWeblogAdapter(Adapter):
    def __init__(self, *args):
        Adapter.__init__(self, *args)
        log.info("Creating metaweblog client with url: %s and username: %s"%(self.url, self.username))
        self.client = MetaWeblogClient(self.url, self.username, self.password)

    def handleMWException(f):
        def new_f(*args):
            try:
                f(*args)
            except MetaWeblogException, e:
                log.error(e)
                raise RubriqueBloggingError(e.message)
        new_f.__name__ = f.__name__
        return new_f



    def authenticate(self):
        pass

    @handleMWException
    def select_blog(self, blogid):
        return self.client.selectBlog(blogid)

    @handleMWException
    def get_posts(self, default_count=20):
           return self.client.getRecentPosts(default_count) 

    @handleMWException
    def publish_draft(self, post):
        self.client.newPost(post, False)

    @handleMWException
    def publish_post(self, post):
        self.client.newPost(post, True)

    @handleMWException
    def get_categories(self):
        return self.client.getCategoryList()

    @handleMWException
    def add_category(self, category):
        pass

    @handleMWException
    def update_post(self, post, publish):
        self.client.editPost(post.id, post,  publish) 

    @handleMWException
    def get_blogs(self):
        return self.client.getUserBlogs()

    @handleMWException
    def upload_media_obj(self, filename=None, fileobj=None):
        self.client.newMediaObject(self, filename, fileobj)


