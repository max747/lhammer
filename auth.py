"""Common login module for web form """

import os
import urllib2
import urllib
import cookielib
from getpass import getpass

class Auth:

    def __init__(self, **paras):
        """ Paras are:
            @cookie_file
            @action         post action of login form
            @user_label     user name label in login form
            @passwd_label
            @other_data     data hidden in login form
        """
        self.paras = paras
        if 'other_data' not in self.paras:
            self.paras['other_data'] = {}

    def login(self):
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPSHandler)
        user = raw_input('User: ')
        passwd = getpass()
        data = {self.paras['user_label']: user, self.paras['passwd_label']: passwd}
        data.update(self.paras['other_data'])
        data = urllib.urlencode(data)
        page = opener.open(self.paras['action'], data)
    
        # Fixme! Should detect if we're login ok
        # if not self.check_login_callback():
        #   return False
        cj.save(self.paras['cookie_file'], ignore_discard = True, ignore_expires= True) # Save cookie
        os.chmod(self.paras['cookie_file'], 0600)
        return True

    def get_opener(self):
        cj = cookielib.LWPCookieJar()
        if not os.path.isfile(self.paras['cookie_file']):
            return None
        cj.load(self.paras['cookie_file'], ignore_discard = True, ignore_expires= True)
        return urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.HTTPSHandler)
