class Blog:
    """Represents blog item
    """    
    def __init__(self):
        self.id = ''
        self.name = ''
        self.url = ''
        self.isAdmin = False

class RubriqueBlogAccount:
    """Represents the settings of a blog account registered with Rubrique
    """
    def __init__(self, blogid, blogname, username, password, homeurl, api_url, apis, preferred, resolved):
        self.blogid = blogid
        self.blogname = blogname.strip()
        self.username = username.strip()
        self.password = password
        self.homeurl = homeurl
        self.api_url = api_url
        if not apis:
            apis = {}
        self.apis = apis
        self.preferred = perferred
        self.resolved = resolved
        self.rubrique_key = self.generate_rubrique_key()

    def generate_rubrique_key(self):
        import re
        import hashlib
        blogname = re.sub('[\W_]+', '', self.blogname)[:5]
        bloghash = hashlib.md5(self.blogname + self.username).hexdigest()
        username = re.sub('[\W_]+', '', self.username)[:5]

        return "%s_%s_%s" %(blogname, username, bloghash)

class User:
    """Represents user item
    """    
    def __init__(self):
        self.id = ''
        self.firstName = ''
        self.lastName = ''
        self.nickname = ''
        self.email = ''
        
class Category:
    """Represents category item
    """    
    def __init__(self):
        self.id = 0
        self.name = ''
        self.isPrimary = False
    
class Post:
    """Represents post item
    """    
    def __init__(self):
        self.id = 0
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


