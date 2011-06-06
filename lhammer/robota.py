
"""A web crawler robot

- Support custom login

"""

import os
import urllib2
import urllib
import urlparse
import cookielib


def login(action, post = None, post_data = None, login_response_event = None):
    """ Login form support
    There are two ways to pass the parameters, use either as you like:

    - post      Dict which contains all the information needed to login,
                urllib.urlencode will be called on the dict for you

    - post_data  Encoded string like that captured by Firefox Liveheader

    A OpenerDirector is returned after the login action is performed,
    you should check whether the login is really OK or not. We could provide
    a callback function for this.

    By default, cookie is not saved, so login is always needed.
    """
    #url = urlparse.urlparse(action)
    #cookie_file = '.'.join(['.cookie', url.netloc.replace('/', '.')])
    cj = cookielib.LWPCookieJar()
    s = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPSHandler)
    s = None
    if post:
        page = s.open(action, urllib.urlencode(post))
    if post_data:
        page = s.open(action, urllib.quote(post_data))

    #self.cj.save(self.cookie_file, ignore_discard = True, ignore_expires= True)
    #self.cj.load(self.cookie_file, ignore_discard = True, ignore_expires= True)
    return s

if __name__ == '__main__':
    pass
