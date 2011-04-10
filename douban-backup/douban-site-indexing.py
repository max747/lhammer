#!/usr/bin/python
# coding: utf-8

"""
The structure of site.douban:

    site -> room -> column -> article or notes

TODO:
    incremental indexing
    nice robots.txt handling
"""

import re
import mechanize
from pyquery import PyQuery as pq
import codecs
import os
import sys
import time
import json
from oodict import OODict

NO_INDEXING_ROOMS = ['索引', '留言板', '工具书', '勘误']

def multipage(fp):
    # Decorator
    def foobar(self, url):
        start = 0
        data = []
        sep = '?' if '?' not in url else '&'
        N = 10
        while True:
            page_url = url + sep + 'start=%d' % start
            #print page_url
            page = fp(self, page_url)
            if not page:
                break # No more data avaiable 
            data += page
            l = len(list(page))
            if l > N:
                l = N
            start += l
        return data
    return foobar

class DoubanSite:

    def __init__(self, url):
        self.url = url
        self.title  = urlopen(self.url).title()
        self.rooms = {}

    def _convert_format(self, links):
        l = []
        for link in links:
            if link.text in ['展开', '[IMG]']:
                continue
            l.append(OODict({'name': link.text, 'url': link.url}))
        return l

    def get_columns(self, room_url):
        br = urlopen(room_url)
        columns = []
        for column in list(br.links(url_regex="\/widget\/articles\/[0-9]+\/$")) +\
                list(br.links(url_regex="\/widget\/notes\/[0-9]+\/$")):
            br.follow_link(column)
            title = br.title().replace('(豆瓣)', '')
            columns.append(OODict({'name': title, 'url': column.url}))
            br.back()
        return columns

    @multipage
    def get_articles(self, column_url):
        br = urlopen(column_url)
        return self._convert_format(list(br.links(url_regex="\/article\/[0-9]+\/$")) + \
               list(br.links(url_regex="\/note\/[0-9]+\/$")))

    def get_rooms(self):
        br = urlopen(self.url)
        rooms = {}
        for room in br.links(url_regex="room"):
            if any(x in room.text for x in NO_INDEXING_ROOMS):
                continue
            rooms[room.text] = OODict({'url': room.url})
        return rooms

    def indexing(self):
        self.rooms = self.get_rooms()
        for name in self.rooms.keys():
            room = self.rooms[name]
            print name, room.url
            room.columns = self.get_columns(room.url)
            for col in room.columns:
                print col.name, col.url
                col.articles = self.get_articles(col.url)
        return self.rooms

br = mechanize.Browser()
br.set_handle_robots(False)
def urlopen(url):
    time.sleep(1)
    try:
        br.open(url)
        return br
    except:
        raise
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: %s site_url' % sys.argv[0]
        sys.exit(-1)

    dbs = DoubanSite(sys.argv[1])
    f = '%s.json' % dbs.title
    if not os.path.exists(f):
        dbs.indexing()
        rooms = dbs.rooms
        fp = open(f, 'w')
        json.dump(dbs.rooms, fp, indent = 4, ensure_ascii = False)
        fp.close()

    rooms = json.load(open(f, 'r'))
    f2 = '%s.txt' % dbs.title
    out = u''
    for name in rooms.keys():
        room = rooms[name]
        out += u'\n【%s】\n\n' % name
        for col in room['columns']:
            out += u'\n●%s\n\n' % col['name']
            if 'articles' not in col:
                continue
            for article in col['articles']:
                if u'●─>' in article['name']:
                    continue
                out += u'%s %s\n' % (article['name'], article['url'])
    open(f2, 'w').write(out.encode('utf8'))
