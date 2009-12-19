#coding: utf8
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import sys
from optparse import OptionParser
from oodict import OODict

M = 1048576
G = M * 1024

desc = []

def init(desc_string):
    """Set args description string"""
    global desc
    desc = desc_string

def parse():
    """Parse all args"""
    args = desc
    parser = OptionParser()
    for arg in args:
        paras = OODict()
        name, paras.help, attr = arg
        short = '-' + name[0]
        long = '--' + name
        if 'store_' in attr: # For store_true, store_false
            paras.default = True
            if 'true' in attr:
                paras.default = False
            paras.action = attr
        parser.add_option(short, long, **paras)

    (opt, _) = parser.parse_args()
    conf = OODict()
    for arg in args:
        name, help, attr = arg
        v = getattr(opt, name)
        if v == None and 'optional' not in attr:
            print 'Required', name
            parser.print_help()
            sys.exit(-1)
            
        if 'int' in attr:	
            try:
                v = size2byte(v)
            except:
                print 'Expect int', name
                sys.exit(-1)

        if 'list' in attr: # Expect multi values
            v = v.split(',')

        conf[name] = v
    return conf

def size2byte(s):
    if not s:
        return None
    if s.isdigit():
        return int(s)

    size=s[:-1]
    unit=s[-1].lower()
    if not size.isdigit():
        return None

    size = int(size)
    weight ={
    'k': 1024, 'm': 1024 * 1024, 'g': 1024 ** 3,
    't': 1024 ** 4, 'p': 1024 ** 5
    }
    if unit not in weight.keys():
        return None
    return size * weight[unit]

def value_filter(opt, values):
    """过滤opt
    检验逗号分割的opt参数是否在values取值范围之内，返回有效的值集。如果opt为空，则返回values
    注意： 非法值被自动忽略，而不是引起程序退出	
    """
    if not opt:
        return values
    v = []
    for item in opt.split(','):
        if item not in values:
            print 'Unknown item %s, ' % item, ' valid values are', values
            continue
        if item not in v:
            v.append(item)
    return v
