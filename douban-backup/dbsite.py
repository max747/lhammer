#!/usr/bin/python
# coding: utf-8

"""
The structure of site.douban:

    site -> room -> column -> article

    site -> 日记 -> note

Requires:
    pyquery, mechanize, pandoc

"""

import re
import mechanize
from pyquery import PyQuery as pq
import codecs
import os
import sys
import time

import oodict

site = oodict.OODict()

def multipage(fp):
    # Decorator
    def foobar(url):
        start = 0
        data = []
        sep = '?' if '?' not in url else '&'
        N = 10
        while True:
            page_url = url + sep + 'start=%d' % start
            #print page_url
            page = fp(page_url)
            if not page:
                break # No more data avaiable 
            data += page
            l = len(list(page))
            if l > N:
                l = N
            start += l
        return data
    return foobar

def get_columns(room):
    br = mechanize.Browser()
    br.open(room)
    return list(br.links(url_regex="\/widget\/articles\/[0-9]+\/$"))

@multipage
def get_articles(column):
    br = mechanize.Browser()
    br.open(column)
    return list(br.links(url_regex="\/article\/[0-9]+\/$"))

def sync_article(url, file_name):
    """ Get article at $url, save to file $file_name

    >>> d = pq('测试<a>哈</a>')
    >>> d.text()
    u'\xe6\xb5\x8b\xe8\xaf\x95 \xe5\x93\x88'
    >>> type(d.text())
    <type 'unicode'>
    >>> u'测试 哈'.encode('utf8')
    '\xe6\xb5\x8b\xe8\xaf\x95 \xe5\x93\x88'
    >>> type(u'测试 哈'.encode('utf8'))
    <type 'str'>
    """
    page = pq(url = url)

    # Extract the article content
    data = '<p>' + page('h1').html() + '</p>' # Get the title right, ugly....
    data += page('.book-info').html()
    data += page('.book-content').html()

    # Write to disk
    tmp_file = file_name + '.html'
    codecs.open(tmp_file,'w','latin-1').write(data)

    # Convert to plain txt using pandoc
    cmd = 'pandoc "%s" -t plain -o "%s"' % (tmp_file, file_name)
    print cmd
    os.system(cmd)
    os.remove(tmp_file)
    time.sleep(6)


def sync_room(room, d):
    # Sync all articles in $room to directory $d   
    br = mechanize.Browser()
    br.open(room)
    for column in get_columns(room):
        br.follow_link(column)
        title = br.title().replace('(豆瓣)', '')
        print title, column.url
        br.back()

        column_dir = os.path.join(d, title)
        # Create directory for colume
        if not os.path.exists(column_dir):
            os.makedirs(column_dir)

        for article in get_articles(column.url):
            article_path = os.path.join(column_dir, article.text)
            if os.path.exists(article_path):
                continue # Already exists, no need to download again FIXME: there maybe changes
            print article.text, article.url
            sync_article(article.url, article_path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: %s site_url' % sys.argv[0]
        sys.exit(-1)

    site.url = sys.argv[1]

    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.open(site.url)
    site.title = br.title()
    site.rooms = list(br.links(url_regex="room"))

    for room in site.rooms:
        print 'ROOM', room.text, room.url
        if '索引' in room.text:
            print 'Skipping...'
            continue
        sync_room(room.url, os.path.join(site.title, room.text))
