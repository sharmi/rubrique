import lxml.html as html
from lxml import etree, objectify
from urlparse import urljoin 


class RSDError(Exception):
    def __init__(self, url='',message=''):
        if message: self.message = message
        else:
            self.message = "Url '%s' does not support RSD(Really Simple Discovery)."

    def __str__(self):
        return self.message

def get_rsd(url):
    rsd_url = get_rsd_url(url)
    if rsd_url:
        rsd = load_rsd(rsd_url)
    if rsd is not None:
        return parse(rsd)

def get_rsd_url(url):
    try:
        data = html.parse(url).getroot()
    except IOError, e:
        raise RSDError(message=str(e))
    rsd_nodes = data.xpath('.//link[@type="application/rsd+xml"]')
    if rsd_nodes:
        return rsd_nodes[0].get("href")
    else:
        return urljoin(url, "rsd.xml") 

def load_rsd(rsd_url):
    try:
        rsd = objectify.parse(rsd_url).getroot()
    except IOError, e:
        raise RSDError(message=e.message)
    return rsd


def parse(rsdroot):
    service = rsdroot.service
    name = service.engineName
    homeurl = service.homePageLink
    apis = {}
    preferred = ''
    for api in service.apis.api:
        attrs = api.attrib
        if 'preferred' in attrs and attrs['preferred'] == 'true':
            preferred = attrs['name'].lower()
        apis[attrs['name'].lower()] = {'name': attrs['name'], 'blogID':attrs['blogID'], 'apiLink':attrs['apiLink']}
    return name, homeurl, apis, preferred

if __name__ == "__main__":
    #print get_rsd("http://scrolls.com/wordpress/")
    print get_rsd("http://www.minvolai.com/")
