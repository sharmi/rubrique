import datetime
from elixir import *

metadata.bind = "sqlite:///movies.sqlite"
#metadata.bind.echo = True


class Blog:
    """Represents blog item
    """    
    def __init__(self):
        self.id = ''
        self.name = ''
        self.url = ''
        self.isAdmin = False

    def __str__(self):
        return "'%s' - Blog Id: %s, Url: %s" %(self.name, self.id, self.url)

def generateRubriqueKey(blogname, username):
        import re
        import hashlib
        blogname = re.sub('[\W_]+', '', blogname)[:5]
        bloghash = hashlib.md5(blogname + username).hexdigest()
        username = re.sub('[\W_]+', '', username)[:5]

        return "%s_%s_%s" %(blogname, username, bloghash[:5])


class RubriqueBlogAccount():
    """Represents the settings of a blog account registered with Rubrique
    """
    def __init__(self, blogid, blogname, username, password, homeurl, apiurl, apis, preferred, resolved):
        self.blogid = blogid
        self.blogname = blogname.strip()
        self.username = username.strip()
        self.password = password
        self.homeurl = homeurl
        self.apiurl = apiurl
        if not apis:
            apis = {}
        self.apis = apis
        self.preferred = preferred
        self.resolved = resolved
        self.rubriqueKey = generateRubriqueKey(self.blogname, self.username)


class RubriqueBlogAccountDB(Entity):
    """Represents the settings of a blog account registered with Rubrique
    """
    rubriqueKey = Field(Unicode(20), primary_key=True)
    blogid = Field(Unicode(50))
    blogname = Field(Unicode(100))
    username = Field(Unicode(50))
    password = Field(Unicode(50))
    homeurl = Field(Unicode(100))
    apiurl = Field(Unicode(150))
    _apis = Field(Unicode(400))
    preferred = Field(Unicode(20))
    resolved = Field(Unicode(20))
    Categories = OneToMany('CategoryRec')
    isCurrent = ManyToOne('AppStatus') 

    def _get_apis(self):
        return eval(self._apis)

    def _set_apis(self, apis):
        self._apis = repr(apis)

class User:
    """Represents user item
    """ 
    def __init__(self):
        id = ''
        firstName = ''
        lastName = ''
        nickname = ''
        email = ''
        
class CategoryRec(Entity):
    """Represents category item
    """    
    catId = Field(Integer, required=True)
    name = Field(Unicode(50), default='')
    isPrimary = Field(Boolean, default=False)
    parentId= Field(Integer, default=-1)
    description = Field(Unicode(150), default='')
    blog = ManyToOne(RubriqueBlogAccountDB)

class Category(object):
    def __init__(self):
        self.catId = -1
        self.name = ''
        self.isPrimary = False
        self.parentId = -1
        self.description = ''

class LocalPost(Entity):
    """Represents post item
    """    
    postid = Field(Integer, default=-1)
    title = Field(Unicode(100), default="(Untitled Post)")
    date = Field(DateTime, default=datetime.datetime.now())
    permaLink = Field(Unicode(100), default='')
    description = Field(UnicodeText, default='')
    textMore = Field(UnicodeText, default='')
    excerpt = Field(UnicodeText, default='')
    link = Field(Unicode(100), default='')
    user = Field(Unicode(50), default='')
    allowPings    = Field(Boolean, default=True)
    allowComments = Field(Boolean, default=True)
    status = Field(Unicode(20), default='')
    _categories = Field(Unicode(200), colname='categories', synonym='categories', default=u'')
    _tags = Field(Unicode(200), colname='tags', synonym='tags', default=u'')
    blog = ManyToOne('RubriqueBlogAccountDB')
    isCurrent = ManyToOne('AppStatus') 
    def _set_categories(self, categories):
        self._categories = "<>".join(categories)

    def _get_categories(self):
        if self._categories:
            return self._categories.split('<>')
        else:
            return []
    categories = property(_get_categories, _set_categories)
    def _set_tags(self, tags):
        self._tags = "<>".join(tags)

    def _get_tags(self):
        return self._tags.split('<>')
    tags = property(_get_tags, _set_tags)


class OnlinePost(object):
    """Represents post item
    """ 
    def __init__(self):
        self.postid = ''
        self.title = ''
        self.date = None
        self.permaLink = ''
        self.description = ''
        self.textMore = ''
        self.excerpt = ''
        self.link = ''
        self.categories = []
        self.tags = ''
        self.user = ''
        self.allowPings    = False
        self.allowComments = False
        self.status = ''

    def __str__(self):
        to_return = []
        for item, value in self.__dict__.iteritems():
            to_return.append("%s: %s" %(item, value))
        return "\n".join(to_return)


class AppStatus(Entity):
    currentBlog = OneToOne('RubriqueBlogAccountDB')
    currentPost = OneToOne('LocalPost')

setup_all()
create_all()
