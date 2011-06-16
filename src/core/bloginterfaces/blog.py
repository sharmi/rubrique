import pod

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

class RubriqueBlogAccountPOD(pod.Object):
        def __init__(self, rubriqueAcc):
            pod.Object.__init__(self)
            self.blogid = rubriqueAcc.blogid
            self.blogname = rubriqueAcc.blogname.strip()
            self.username = rubriqueAcc.username.strip()
            self.password = rubriqueAcc.password
            self.homeurl = rubriqueAcc.homeurl
            self.apiurl = rubriqueAcc.apiurl
            self.apis = rubriqueAcc.apis
            self.preferred = rubriqueAcc.preferred
            self.resolved = rubriqueAcc.resolved
            self.rubriqueKey = generateRubriqueKey(self.blogname, self.username)

            
class User:
    """Represents user item
    """    
    def __init__(self):
        self.id = ''
        self.firstName = ''
        self.lastName = ''
        self.nickname = ''
        self.email = ''
        
class Category(object):
    """Represents category item
    """    
    def __init__(self):
        self.name = ''
        self.catId = ''
        self.blog = ''
        self.parentId= ''
        self.isPrimary = False

class BlogCategories(pod.Object):
    def __init__(self):
        pod.Object.__init__(self)
        self.blog = None
        self.catgories = []
        self.lastqueriedtime = None
    

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


class LocalPost(pod.Object):
    def __init__(self):
        pod.Object.__init__(self)
        self.postid = ''
        self.title = '(Untitled Post)'
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

    def __repr__(self):
        to_return = []
        for item, value in self.__dict__.iteritems():
            to_return.append("%s: %s" %(item, value))
        return "\n".join(to_return)

    def __str__(self):
        return str(self.title)



#class RubriqueAppStatus(pod.Object):
#    def __init__(self, state, value):
#        self.state = state
#        self.value = value
