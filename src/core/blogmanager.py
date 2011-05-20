import platform
import os
import logging
from core.lib.sqliteshelf import SQLiteShelf
from core.bloginterfaces.blog import RubriqueBlogAccount, Post
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
        self.__setup_data_path()
        self.blogs = SQLiteShelf(self.dbpath, "blogs")
        self.app_status = SQLiteShelf(self.dbpath, "app_status")
        self.service_apis = {}
        self.posts = {} #
        self.localposts = {} #SQLiteShelf(self.dbpath, "localposts")
        try:
            self.current_blog = self.app_status['current_blog']
        except KeyError:
            self.current_blog = None
        try:
            self.current_post = self.app_status['current_post']
        except KeyError:
            self.current_post = None

     
        
    def __setup_data_path(self):
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

    def resolve_blog(self, url, username, password, blog_id = None):
        try:
            blog_service, homeurl, apis, preferred = rsd.get_rsd(url)
        except rsd.RSDError, e:
            raise RubriqueBlogSetupError("Failed to resolve blogtype. Manual entry required. Error Message as follows '%s'" %e)
            return -1
        api_url = apis[preferred]['apiLink']
        blogtype = preferred
        blogid = apis[preferred]['blogID']
        resolved_blogtype = self._resolve(blogtype)
        service_api = self._service_api_factory(resolved_blogtype, api_url, username, password)
        blogs =  service_api.get_blogs()
        blogacc = None
        if not blogs:
            raise RubriqueBlogSetupError("Api is Unaware of any blogs")
        if len(blogs) == 1:
            blogacc = RubriqueBlogAccount(blogs[0].id, blogs[0].name, blogs[0].url, api_url, apis, preferred, resolved_blogtype)

        elif blog_id:
            for blog in blogs:
                if blog.id == blogid:
                    blogacc = RubriqueBlogAccount(blogs[0].id, blogs[0].name, blogs[0].url, api_url, apis, preferred, resolved_blogtype)
        else:
            #TODO User should select blog
            pass
        if blogacc:
            self.blogs[blogacc.rubrique_key] = blogacc
            return blogacc
        else:
            raise RubriqueBlogSetupError("The apis do not have a blog matching blogid '%s'" %(blogid))

    def _resolve(self, blogtype):
        if blogtype in [METAWEBLOG, WORDPRESS]: 
            return METAWEBLOG
        else:
            raise RubriqueBlogSetupError("BlogType " + blogtype + " is not supported")

    def _service_api_factory(self, blogtype, api_url, username, password):
        if blogtype  == METAWEBLOG: 
            return adapter.MetaWeblogAdapter(api_url, username, password)
        else:
            raise RubriqueBlogSetupError("BlogType " + blogtype + " needs to be resolved")

    def add_blog():
        pass

    def set_current_blog(self, rubrique_key):
        self.current_blog = self.blogs[rubrique_key]
        if rubrique_key not in self.posts:
            self.posts[rubrique_key] = SQLiteShelf(self.dbpath, "posts_"+rubrique_key)
        if rubrique_key not in self.localposts:
            self.localposts[rubrique_key] = SQLiteShelf(self.dbpath, "localposts_"+rubrique_key)
        if rubrique_key not in self.categories:
            self.categories[rubrique_key] = SQLiteShelf(self.dbpath, "categories_"+rubrique_key)

    def get_latest_posts(self, num=10):
        return self.current_blog.getRecentPosts(num)
        
    def publish(self,  post):
        self.current_blog.newPost(post,  True)

blogManager = BlogManager()
def getBlogManager():
    return blogManager
