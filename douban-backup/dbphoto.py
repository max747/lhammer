#!/usr/bin/python
"""Download douban album to local folder """

import os
import sys

import douban
douban.verbose = True

if len(sys.argv) < 2:
    print 'Usage: %s album_id' % sys.argv[0]
    print '    http://www.douban.com/photos/album/$album_id/'
    sys.exit(-1)

db = douban.DoubanCrawler()
album = sys.argv[1]

if not os.path.exists(album):
    print 'Creating local album folder', album
    os.mkdir(album)

photos = db.get_album_photos(album)
print len(photos), 'photos'
for p in photos:
    url = p.thumb.replace('thumb', 'photo')
    local_file = os.path.join(album, os.path.basename(url))
    if os.path.exists(local_file):
        continue

    print url
    fp = open(local_file, 'w')
    fp.write(douban.download(url))
    fp.close()
print 'done'
