#!/usr/bin/python
#coding: utf8
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

""" DoubanCrawler
Extract informations not provided by DoubanAPI from the html pages

Jaime Chen<nkchenz@gmail.com>
"""
import time
import urllib2
import re

from oodict import OODict

verbose = False
def debug(msg):
    if verbose:
        print msg

def download(url):
    time.sleep(1) # Be nice if you don't want to be baned by douban.com
    debug(url)
    try:
        return urllib2.urlopen(url).read()
    except urllib2.HTTPError, err:
        #if  err.code == 404: # Page not found
        #    return None
        return None
    except urllib2.URLError:
        return None

class DoubanCrawler:

    def __init__(self):
        self.ROOT_URL = 'http://www.douban.com'

        self.PATTERNS = {
        'album':
            ('/photos/album/([0-9]+)/.*?src="(.*?)".*?/photos/album/.*?>(.*?)</a>',
            ['id', 'cover', 'desc']),
            
        'photo': ('/photos/photo/([0-9]+)/".*?src="(.*?)"' , ['id', 'thumb']),
        'title': ('<title>(.*?)</title>', ['title']),
        }

        """
        'subject':  '/subject/([0-9]+)/.*?title="(.*?)"', # For books, movies. Get the id and title
        'people': '/people/(.{1,30})/',
        'friend': '/people/(.{1,30})/"><img src="(.*?)".*?alt="(.*?)"',
        'group': '"/group/(.{1,30})/"><img src="(.*?)".*?alt="(.*?)"',
        'doulist': '/doulist/(.*?)/">(.*?)</a>',

        'saying': '<li class="mbtr">(.*?)</li>',
#'rec': '<li class="mbtr">(.*?)</li>',
        'rec': '<li .*?(推荐.*?回应)',
        'doulist_desc': '<div class="indent">(.*?)</div>', # For the description of doulist,
        'total':  '共(.*?)个条目',
        """

    def _get_url(self, *parts):
        """Generate abosolute url for this site"""
        return '/'.join([self.ROOT_URL] + list(parts))

    def get_user_info(self, user):
        home = self._get_url('people', user)
        html = download(home)
        if not html:
            return None
        return user

    def get_albums(self, user = None):
        """Get all my albums"""
        #if not user:
        #    user = me
        url = self._get_url('people', user, 'photos')
        return self._extract(self.PATTERNS['album'], url)

    def _get_title(self, url):
        return self._extract(self.PATTERNS['title'], url)[0]['title']

    def get_album_photos(self, album):
        """Get all photos of an album
        
        Return: dict(url, title, photos)
        """
        data = OODict()
        data.url = self._get_url('photos/album', album)
        data.title = self._get_title(data.url)
        data.photos =  self._extract_multi_pages(self.PATTERNS['photo'], data.url)
        return data

    def _extract_multi_pages(self, pattern, url):
        start = 0
        data = []
        while True:
            page = self._extract(pattern, url, start)
            if not page:
                break # No more data avaiable 
            data += page
            start += len(page)
        return data

    def _extract(self, pattern, url, start = 0):
        """How to get page_size?"""
        data = []

        # Replacing '?' in url
        if start:
            seprator = '?'
            if seprator in url:
                seprator = '&'
            url = url + seprator + 'start=%d' % start

        page = download(url)

        matches = re.findall(pattern[0], page.replace('\n', ''))
        if not matches:
            return None

        # Change the matching results to meaningful fields
        for m in matches:
            # m is supposed to be a tuple, so is pattern[1] which is supposed
            # to a list
            if not isinstance(m, tuple):
                m = [m.strip()]

            entry = OODict()
            for k, v in zip(pattern[1], m):
                entry[k] =  v
            data.append(entry)

        return data
