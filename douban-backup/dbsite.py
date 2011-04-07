#!/usr/bin/python
# coding: utf-8

"""
The structure of site.douban:

    site -> room -> column -> article

    site -> 日记 -> note

"""

import re
import mechanize
from pyquery import PyQuery as pq

import oodict

site = oodict.OODict()
site.url = 'http://site.douban.com/106369/'

br = mechanize.Browser()
br.open(site.url)
site.title = br.title()

site.rooms = list(br.links(url_regex="room"))


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

def get_content(article):
    html = pq(url = article)
    c = html('.book-content')
    txt = c.text()
    txt = txt.encode('utf8')
    fp = open('a.txt', 'w+')
    fp.write(txt)
    fp.close()

article = 'http://site.douban.com/widget/articles/11971/article/12191447/'
article = 'http://site.douban.com/widget/articles/11971/article/11138094/'
get_content(article)

"""

for room in site.rooms:
    print 'ROOM', room.text, room.url
    for column in get_columns(room.url):
        br.follow_link(column)
        title = br.title().replace('(豆瓣)', '')
        print title, column.url
        br.back()

        for article in get_articles(column.url):
            print article.text, article.url
    break

room = 'http://site.douban.com/106369/room/1532/'
get_articles(room)

article = 'http://site.douban.com/widget/articles/11971/'
for note in get_notes(article):
    print note.text
"""
