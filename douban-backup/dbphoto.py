#!/usr/bin/python
"""Download douban album to local folder """

import os
import sys

import douban

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
total = len(photos)
print total, 'photos'
n = 1
for p in photos:
    url = p.thumb.replace('thumb', 'photo')
    local_file = os.path.join(album, os.path.basename(url))
    if os.path.exists(local_file):
        continue

    print '%d/%d' % (n, total) , local_file
    img = douban.download(url)
    fp = open(local_file, 'w')
    fp.write(img)
    fp.close()

    n += 1
print 'done'
