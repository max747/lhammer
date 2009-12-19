#!/usr/bin/python
#coding: utf8

"""
CopyRight (C) 2008 Chen Zheng <nkchenz@gmail.com> 
Distributed under terms of GPL v2

Generate ed2k hashs for files, store in ~/.p2pz. First lookup in the file, if not
found, compute then.

Examples:
ideer@ideer:/home/chenz/source/dhtlist$ ./p2pz.py /chenz/aMule/Incoming/BS/The.Godfather.*
99%     2792/2797     ok
The.Godfather.1972.BDRip.X264-TLF.mkv sha1:c40c60c5153967cbeb742d784c6c3dee9115fd0c md4:a7835c7ed5839cfcd15b544daa2d013a
99%     2793/2797     ok
The.Godfather.II.1974.BDRip.X264-TLF.mkv sha1:39b19a80d8505480b426b3a526e5ab9f36583fb9 md4:f9a4a3e7faa0e91b8a3f8d637fb73395
 0%        0/1        ok
The.Godfather.II.1974.BDRip.X264-TLF.srt sha1:de2725a619db365b0c8ad3236a1498293add3ba0 md4:aaf70a49e753d79eeda0b18d2e5ab833
ideer@ideer:/home/chenz/source/dhtlist$ ./dhtlist.py /chenz/aMule/Incoming/BS/The.Godfather.*
The.Godfather.1972.BDRip.X264-TLF.mkv sha1:c40c60c5153967cbeb742d784c6c3dee9115fd0c md4:a7835c7ed5839cfcd15b544daa2d013a
The.Godfather.II.1974.BDRip.X264-TLF.mkv sha1:39b19a80d8505480b426b3a526e5ab9f36583fb9 md4:f9a4a3e7faa0e91b8a3f8d637fb73395
The.Godfather.II.1974.BDRip.X264-TLF.srt sha1:de2725a619db365b0c8ad3236a1498293add3ba0 md4:aaf70a49e753d79eeda0b18d2e5ab833

Given piece of data of any length, and file's hash, is there a way to verify whether
the data belongs to the file or not?
"""

import os
from oodict import *
import sys
import hashlib
from binascii import hexlify, unhexlify
import pprint
#import md4

HASH_ALGOS = ['md4', 'sha1']
#CHUNK_SIZE = 2 ** 26 # 64M
CHUNK_SIZE = 9728000
FileList = os.path.expanduser('~/.p2pz')

def secure_hash(algo, data):
    hash = hashlib.new(algo)
    hash.update(data)
    # Return hex string of hash value for general using
    return hash.hexdigest()

def size2m(size):
    M = 1024 * 1024
    if size < M:
        return 1
    return size / M

def show_progress(p, total):
    print '\r%2d%% %8d/%-8d' % (p * 100 / total, p, total),
    sys.stdout.flush()
    
def digest(file, algos):
    """Compute different algorithm hashs at one pass, return an oodict for each"""
    try:
        meta = os.stat(file)    
    except:
        print 'stat error', file
        return None
    r = OODict()
    for algo in algos:
        info = OODict()
        info.size = meta[6]
        info.chunksize = CHUNK_SIZE
        info.name = [os.path.basename(file)]
        info.roothash = ''
        info.hashlist = []
        info.algorithm = algo 
        r[algo] = info

    f = open(file, 'rb')
    remain_len = meta[6]
    total = size2m(meta[6])
    while True:
        data = f.read(CHUNK_SIZE)
        if not data:
            return None # File read error
        
        for algo in r.keys():
            r[algo].hashlist.append(secure_hash(algo, data))

        copied = total - size2m(remain_len)
        show_progress(copied, total)
        remain_len -= len(data)
        if remain_len <= 0:
            break
    
    f.close()
    
    # If there is only one chunk, don't bother to hash again
    for algo, info in r.items():
        if len(info.hashlist) == 1:
            info.roothash = info.hashlist[0]
        else:
            # Need to change hex hash back to binary value
            info.roothash = secure_hash(algo, ''.join(map(lambda hash: unhexlify(hash), info.hashlist)))

    print 'ok'
    return r


def save(data):
    if os.path.isfile(FileList):
        os.system('cp %s %s.old' %(FileList, FileList))
    open(FileList, 'w+').write(pprint.pformat(data))

def load(file):
    box = {}
    if os.path.isfile(file):
        box = eval(open(file, 'r').read())
    return box

def print_hash(file):
    name = os.path.basename(file)
    print name,
    hashs = mybox[name]
    for algo, hash in hashs.items() :
        print '%s:%s' % (algo, hash),
    print

def hash_file(file):
    name = os.path.basename(file)
    if name in mybox: # Already hashed
        return 

    r = digest(file, HASH_ALGOS)
    mybox[name] = {}
    for algo, info in r.items():
        mybox[name][algo] = info.roothash       # Save filename -> key
        if info.roothash not in mybox:
            mybox[info.roothash] = info   # Save key -> file meta info
        else:
            mybox[info.roothash]['name'].append(name) # Duplicated file
    return

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print 'Usage: ', sys.argv[0], ' file'
        sys.exit(-1)

    mybox = load(FileList)
    for f in sys.argv[1:]:
        if not os.path.isfile(f):
            continue
        hash_file(f)
        print_hash(f)
        save(mybox)
