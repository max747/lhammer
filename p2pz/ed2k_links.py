#!/usr/bin/python

# Give me a .pzpz file, I'll give you a much smaller file contains ed2k link only


import p2pz
import sys
import pprint

newbox = {}

mybox = p2pz.load(sys.argv[1])
for k,v in mybox.items():
    if 'roothash' in v:
        if 'algorithm' in v and v['algorithm'] == 'md4':
            del v['algorithm']
            del v['chunksize']
            del v['hashlist']
            newbox[k] = v
        # Throw sha1 infos
    else:
        newbox[k] = v

#pprint.pprint(newbox)
for k,v in newbox.items():
    if 'md4' in v:
        info = newbox[v['md4']]
        print 'ed2k://|file|%s|%s|%s|/|sha1:%s|' % (','.join(info['name']), info['size'], info['roothash'], v['sha1'])
