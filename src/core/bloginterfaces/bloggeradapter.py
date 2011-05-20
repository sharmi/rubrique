from urlparse import urlparse
from gdata import service
import gdata
import atom
from adapter import Adapter
class BloggerAdapter(Adapter):

    def __init__(self, username, password, url):
        Adapter.__init__(self, username, password, url)

    def authenticate():
        blogger_service = service.GDataService(self.username, self.password) #username as email address
        blogger_service.source = "MinVolai-Rubrique-0.1"
        blogger_service.service = 'blogger'
        blogger_service.account_type = 'GOOGLE'
        blogger_service.server = urlparse(url).netloc #usually www.blogger.com
        blogger_service.ProgrammaticLogin()
       
    def PrintUserBlogTitles(blogger_service):
        query = service.Query()
        query.feed = '/feeds/default/blogs'
        feed = blogger_service.Get(query.ToUri())

        print feed.title.text
        for entry in feed.entry:
            print "\t" + entry.title.text 
