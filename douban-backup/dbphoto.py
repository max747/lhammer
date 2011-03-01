#!/usr/bin/python
"""Download douban album to local folder """

import os
import sys

import douban

if len(sys.argv) < 2:
    print 'Usage: %s album_id' % sys.argv[0]
    print '    http://www.douban.com/photos/album/$album_id/'
    print 'Will create a folder under "albums" by default'
    sys.exit(-1)

db = douban.DoubanCrawler()
album = sys.argv[1]
data = db.get_album_photos(album)

root = os.path.join('albums', '%s-%s' % (album, data.title))
if not os.path.exists(root):
    print 'Creating local album folder', root
    os.makedirs(root)

total = len(data.photos)
print total, 'photos'
n = 0
for p in data.photos:
    n +=1
    url = p.thumb.replace('thumb', 'photo')
    local_file = os.path.join(root, os.path.basename(url))
    if os.path.exists(local_file):
        continue

    print '%d/%d' % (n, total) , local_file
    img = douban.download(url)
    fp = open(local_file, 'w')
    fp.write(img)
    fp.close()

print 'done'
