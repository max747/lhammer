#!/usr/bin/python
#coding: utf8
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

"""
douban-backup: douban backup script for user data
CopyRight (C) 2009 Chen Zheng <nkchenz@gmail.com> 
Distributed under terms of GPL v2
"""

import urllib2
import re
import sys
import time
from oodict import OODict
import args
from HTMLParser import HTMLParser

URL_DOUBAN = 'http://www.douban.com'
#For books, movies, musics
URL_LIST = 'http://www.douban.com/%s/list' 
#For doulist content
URL_DOULIST = 'http://www.douban.com/doulist'
PATTERNS = {
'subject':  '/subject/([0-9]+)/.*?title="(.*?)"', # For books, movies. Get the id and title
'people': '/people/(.{1,30})/',
'friend': '/people/(.{1,30})/"><img src="(.*?)".*?alt="(.*?)"',
'group': '"/group/(.{1,30})/"><img src="(.*?)".*?alt="(.*?)"',
'doulist': '/doulist/(.*?)/">(.*?)</a>',

'saying': '<li class="mbtr">(.*?)</li>',
#'rec': '<li class="mbtr">(.*?)</li>',
'rec': '<li .*?(推荐.*?回应)',
'title':  '<title>(.*?)</title>',
'doulist_desc': '<div class="indent">(.*?)</div>', # For the description of doulist,
'total':  '共(.*?)个条目',
}

def mkurl(*parts):
    return '/'.join(list(parts))

def douban_url(type, id):
    return mkurl(URL_DOUBAN, type, id)

def obj2xml(o, name):
    """Change a object to xml format string"""
    xml = '<%s>\n' % name

    if isinstance(o, dict):
        for k, v in o.items():
            if k.startswith('_'):
                continue
            xml += obj2xml(v, k)
    else:
        if isinstance(o, list):
            for item in o:
                xml += obj2xml(item, 'entry')
        else:
            xml += str(o)
    xml += '</%s>\n' % name
    return xml


def debug(msg):
    print >>sys.stderr, msg
    pass

error = debug

class Downloader:
    """
    Get web pages for the internet, return html contents

    Need to handle network errors
    """ 
    def get(self, url):
        time.sleep(1) # Be nice if you don't want to be baned by douban.com
        debug('Downloading ' + url)
    
        try:
            return urllib2.urlopen(url).read()
        except urllib2.HTTPError, err:
            if  err.code == 404: # Page not found
                return None
            else:
                raise

class Matcher:
    """Find patterns in the given data, you must feed data first and then
    you can do as many finds as you want"""
    def feed(self, data):
        self.data = data

    def find(self, pattern):
        matches = re.findall(pattern, self.data.replace('\n', ''))
        if not matches:
            return None
        if len(matches) == 1:
            return matches[0]
        else:
            return matches


class Converter(HTMLParser):
    """Small converter for html2text"""
    def html2text(self, html):
        if not html:
            return ''
        self.text = ''
        HTMLParser.feed(self, html)
        return self.text

    def handle_data(self, data):
        self.text += data


class MultiPagesReader:
    '''
    Read multi pages url to self.data

    Maybe you want to reimplement the handle_header, handle_page function
    '''

    def __init__(self):
        self.downloader = Downloader()
        self.matcher = Matcher()
        self.converter = Converter()
        self.generator = Generator()
    
    def read(self, url, pattern, single_page = False, max_pages = None):
        """Read url for at most max_pages, if the number is not given, 
        read all by default"""
        self.pos = 0
        self.total = 0

        # Init private data for this read
        self.data = OODict()
        self.data.url = url
        self.data.title = ''
        self.data.entries = []

        self.entry_pattern = PATTERNS[pattern]
        self.handle_entry = getattr(self.generator, 'build_' + pattern)

        while True:
            page = self.next_page()
            self.matcher.feed(page)

            if self.pos == 0:
                self.handle_header()
            # n entries found
            n = self.handle_page()
            if single_page:
                break

            # Empty page is considered as a sign for no more pages
            if n <= 0:
                break
            # Update the number of entries we read
            self.pos += n

            # Check if we have a valid 'total' and compare it with number read
            if self.total > 0 and self.pos >= self.total:
                    break # All read

        #self.data.n = len(self.data.entries)
        return self.data

    def handle_header(self):
        """Get the information on the first page"""
        self.data.title = self.matcher.find(PATTERNS['title'])
        # Try to get total number of entries at the first page
        total = self.matcher.find(PATTERNS['total'])
        if total:
            self.total = int(total)

    def handle_page(self):
        """Parse each entry in one page, return number of entries found"""
        matches = self.matcher.find(self.entry_pattern)
        if matches:
            if isinstance(matches, tuple): # Only one entry found
                entries = [matches]
            else:
                entries = list(set(matches))
            for entry in entries: # Give each value a name
                self.data.entries.append(self.handle_entry(entry))
            return len(entries)
        else:
            return 0


    def next_page(self):
        # If there is already some args in the url, we can't use '?' any more, or it will be error
        c = '?'
        if c in self.data.url:
            c = '&'
        return self.downloader.get(self.data.url + c + 'start=%d' % self.pos)


class Generator:
    """Build a dict using the given tuple in matching results"""

    def build_subject(self, entry):
        url = douban_url('subject', entry[0])
        return OODict({'id': entry[0], 'title': entry[1], 'url': url})

    def build_friend(self, entry):
        url = douban_url('people', entry[0])
        return OODict({'id': entry[0], 'img': entry[1], 'name': entry[2], 'url': url})

    def build_group(self, entry):
        url = douban_url('group', entry[0])
        return OODict({'id': entry[0], 'img': entry[1], 'name': entry[2], 'url': url})

    def build_doulist(self, entry):
        url = douban_url('doulist', entry[0])
        return OODict({'id': entry[0], 'title': entry[1], 'url': url})

    def build_rec(self, entry):
        """Unstructed rec data"""
        return '<![CDATA[%s]]>' % entry

    def build_saying(self, entry):
        """Unstructed rec data"""
        return '<![CDATA[%s]]>' % entry
        #return OODict({'id': entry[0], 'title': entry[1], 'url': url})


class DouListReader(MultiPagesReader):

    # We just need reimplement this to get the description for doulist    
    def handle_header(self):
        MultiPagesReader.handle_header(self) # Call the orignal to get 'title' and 'total'
        self.data.description = self.converter.html2text(self.matcher.find(PATTERNS['doulist_desc']))


class User(OODict):
    """
    User class for douban, name can be given at creating time or set later
    """

    def __init__(self, name = ''):
        self.name = name
        self.url = douban_url('people', self.name)
        self._downloader = Downloader()
        self._converter = Converter()
        self._matcher = Matcher()
        self._doulist_loader = DouListReader()
        # If we use the same loader, it's not thread safe
        self._normal_loader = MultiPagesReader() # Normal multipage loader

        self._items = ['doulists', 'books', 'movies', 'musics', 'groups', 'friends', 'recs', 'saying']

    def exists(self):
        home = douban_url('people', me.name)
        html = self._downloader.get(home)
        if not html:
            return False 
        else:
            return True

    def get(self, items):
        if 'all' in items:
            items = self._items
        for item in items:
            handler = 'get_' + item
            if item not in self._items or not hasattr(self, handler):
                error('item %s not supportted yet' % item)
                continue
            debug('Getting ' + item)
            getattr(self, handler)()

    def get_doulist(self, id):
        url = '/'.join([URL_DOULIST, str(id)])
        dl = self._doulist_loader.read(url, 'subject')
        dl.id = id
        return dl

    def get_doulists(self):
        self.doulists = self._normal_loader.read(mkurl(self.url, 'doulists'), 'doulist')
        # Load all doulists
        entries = []
        for dl in self.doulists.entries:
            entries.append(self.get_doulist(dl.id))
        self.doulists.entries = entries
        
    def get_books(self):
        self._get_generic('books')

    def _get_generic(self, item):
        self[item] = {}
        tmpitem = item
        if item.endswith('s'):
            tmpitem = item[:-1] # Change 'books' to 'book'. silly urls!
        for status in ['do', 'wish', 'collect']:
            self[item][status] = self._normal_loader.read(mkurl(URL_LIST % tmpitem, self.name, status), 'subject')

    def get_movies(self):
        self._get_generic('movies')

    def get_musics(self):
        self._get_generic('musics')

    def get_friends(self):
        self.friends = self._normal_loader.read(mkurl(self.url, 'friend_list'), 'friend', True)

    def get_groups(self):
        self.groups = self._normal_loader.read(mkurl(self.url, 'groups'), 'group', True)
    
    def get_recs(self):
        self.recs = self._normal_loader.read(mkurl(self.url, 'recs'), 'rec')

    def get_saying(self):
        self.saying = self._normal_loader.read(mkurl(self.url, 'miniblogs?type=saying'), 'saying')

    #recs, miniblogs, reviews, subjects, online, recs

if __name__ == '__main__':

    args.init([
        ('user', 'user name to backup', ''),
        #('minbs', '最小块大小', 'int'),
        ('item', 'data items to backup, seperated by comma, default \'all\'', 'list'),
        #('stride_count', '条带数目, 用于stride模式，默认为1', 'int optional'),
        #('file', '测试用的文件名字，不提供的话会自动创建', 'optional'),
        ])
    conf = args.parse()
    me = User(conf.user)
    if not me.exists():
        error('user %s not exists' % conf.user)
        sys.exit(-1)
    print "<?xml version='1.0' encoding='UTF-8'?>\n"
    me.get(conf.item)
    print obj2xml(me, 'user')
    sys.exit(0)
