"""Web form authentication helper

Example:

Edit your config file to suit the login form of your web site, like this:

    {"action": "https://www.xxxx.com/login",
    "username": "zhengchen",
    "password": "*******",
    "url": "https://www.xxx.com/index"}

'url' is an example for additional informations required by server, you
should put all of them here.
And the code:

    import auth
    test = auth.AuthenticationHelper('test.auth')
    test.login()
    opener = test.get_opener()
"""

import os
import urllib2
import urllib
import urlparse
import cookielib
import json


def login():
    return opener

class AuthenticationHelper:

    def __init__(self, config):
        """ File 'config' is in json format, contains the informations about
        the login form.
        """
        if not os.path.exists(config):
            raise IOError('Config file required')
        self.paras = json.load(open(config, 'r'))

        url = urlparse.urlparse(self.paras['action'])
        tmp = url.netloc + os.path.join(url.path, 'cookie').replace('/', '.')
        self.cookie_file = os.path.join(os.path.expanduser('~/.' + tmp))

        self.cj = cookielib.LWPCookieJar()

    def login(self):
        """Perform the login and save cookies for further use """
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj), urllib2.HTTPSHandler)
        page = opener.open(self.paras['action'], urllib.urlencode(self.paras))

        # Fixme! Should detect if we're login ok
        # if not self.check_login_callback():
        #   return False

        self.cj.save(self.cookie_file, ignore_discard = True, ignore_expires= True)
        print 'Login ok'
        return True

    def get_opener(self):
        """Return an urllib2.OpenerDirector object that you can play with"""
        if not os.path.exists(self.cookie_file):
            return None # Not login
        self.cj.load(self.cookie_file, ignore_discard = True, ignore_expires= True)
        return urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj), urllib2.HTTPSHandler)

if __name__ == '__main__':
    pass
