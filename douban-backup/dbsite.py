#!/usr/bin/python
# coding: utf-8

import re
import mechanize

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

def get_articles(room):
    br = mechanize.Browser()
    br.open(room)
    return list(br.links(url_regex="\/widget\/articles\/[0-9]+\/$"))

@multipage
def get_notes(article):
    br = mechanize.Browser()
    br.open(article)
    return list(br.links(url_regex="\/article\/[0-9]+\/$"))

for room in site.rooms:
    print 'ROOM', room.text, room.url
    for article in get_articles(room.url):
        br.follow_link(article)
        title = br.title().replace('(豆瓣)', '')
        print title, article.url
        br.back()

        for note in get_notes(article.url):
            print note.text, note.url

"""
room = 'http://site.douban.com/106369/room/1532/'
get_articles(room)

article = 'http://site.douban.com/widget/articles/11971/'
for note in get_notes(article):
    print note.text
"""
