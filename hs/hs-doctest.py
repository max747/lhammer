#!/usr/bin/python

"""
hs-doctest: doctest tool for haskell
CopyRight (C) 2008 Chen Zheng <nkchenz@gmail.com> 
Distributed under terms of GPL v2

Testcase must begin with '> ', followed by its output, like test1. If nothing is between 
two tests, means the first test has no output, like test2. Output is terminated by a blank
line, like test3, its output is only '[2]'.

{-
> test1 [1, 2]
1
> test2
> test3 [1, 2]
[2]

This is not output of test3
> test4
<BLANKLINE>
> test5
-}

You can use '<BLANKLINE>' to represent a blankline in output, like test4.


We start a new ghci thread, use ':load testfile' loading the whole file first, 
then run each test case by writting them to ghci thread line by line, after that, 
outputs are checked.

The reason why we dont load source code line by line is that,  if we do, it's 
diffcult for ghci to understand the multi-line function declarations.
  
Notice that We automatically add a prefix 'let ' for declarations in test cases,
    > a = [1, 2]
command sent to ghci will be 'let a = [1, 2]'

"""

PROMPT = '> ' # Prompt recognized in comments
HI_PROMPT = 'Prelude> '
MODULE_PROMPT = '*Main> ' # After load source file, module context
marks = [MODULE_PROMPT, HI_PROMPT]
HI = 'ghci ' # Haskell  Interpreter

import sys
import os
import fcntl
import subprocess

if len(sys.argv) < 2 :
    print 'Usage: hs-doctest *.hs [function]'
    sys.exit(-1)

f = sys.argv[1]
if not os.path.isfile(f):
    print f, 'not found'
    sys.exit(-1)

function = ''
if len(sys.argv) == 3:
    function = sys.argv[2]

def extract_tests_from_line(line, result):
    """
    If is_output is True, means we are expecting the output of last test case. 
    If we return True, means we are still expecting more output
    """
    if line.startswith(PROMPT):
            if 'current' in result:
                result['cases'].append(result['current']) # Save the old test case
            result['current'] = {'cmd': line[len(PROMPT):], 'output': ''}
            result['expecting_output'] = True
            return

    if not result['expecting_output']:
        return

    if not line: # Blank line, terminator of test output
        result['cases'].append(result['current'])
        del result['current'] # After adding, delete it
        result['expecting_output'] = False
        return 

    if line == '<BLANKLINE>':
        line = ''
    result['current']['output'] += line + '\n' # Maybe need change to '\r\n' under win   
    return


def extract_tests(f):
    is_comment = False
    tests = {}
    tests['cases'] = []
    tests['expecting_output'] = False
    for line in open(f).readlines():
        line = line.strip()

        if line.startswith('--'):
            comment = line[2:]
            comment = comment.strip()
            extract_tests_from_line(comment, tests)
            continue

        # Block comment
        if line == '{-':
            is_comment = True
            continue
        if line == '-}':
            is_comment = False
            continue
        if is_comment:
            extract_tests_from_line(line, tests)
        else:
            tests['expecting_output'] = False
            if 'current' in tests:
                tests['cases'].append(tests['current']) # Save the old test case
                del tests['current']
    return tests

def search_for_marks(fp, marks):
    # Search for a mark in stream, wait until found, streams maybe blocked if nothing to read
    data = ''
    mark = ''
    while True:
        # Is there a efficient way to do this? 
        #Becareful, if you read more than you can get, you may hang up
        c = fp.read(1) 
        if not c:
            return (mark, data)
            break # File ending
        data += c
        for mark in marks:
            ml = len(mark)
            if len(data) >= ml and data[-ml:] == mark:
                    # Can't use break here, because it only breaks 'for', not 'while'
                    return (mark, data[:-ml]) # Found 

def run_cmd(p, cmd):
    p.stdin.write('%s\n' % cmd)
    mark, data = search_for_marks(p.stdout, marks)
    # Read Exceptions if there are any, there maybe problems about orders about lines of stdout and stderr
    return data + read_non_block(p.stderr)


def read_non_block(fp):
    # For stderr reading
    flags = fcntl.fcntl(fp, fcntl.F_GETFL)
    fcntl.fcntl(fp, fcntl.F_SETFL, os.O_NONBLOCK)
    data = ''
    while True:
        try:
            line = fp.readline()
            if not line:
                break
            data += line
        except IOError:
            break
    fcntl.fcntl(fp, fcntl.F_SETFL, flags)
    return data

tests = extract_tests(f)

PIPE = -1
hi = subprocess.Popen(HI, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE, bufsize = 1)
mark, data = search_for_marks(hi.stdout, marks)
print data
print run_cmd(hi, ':load ' + f)

ok, fail = 0, 0
print
for test in tests['cases']:
    cmd, output = test['cmd'], test['output'].rstrip()

    if not cmd.startswith(function):
        continue

    if '=' in cmd:     # Fixme! what if '=' in a string?
        cmd = 'let ' + cmd
    print '%s%s' % (PROMPT, cmd)
    print 'Expect:'
    print output
    got = run_cmd(hi, cmd).rstrip()
    if got == output:
        print 'OK'
        ok += 1
    else:
        fail += 1
        print 'Got:'
        print got
        print 'FAIL'
        
    print 
print '%d passed, %d failed' % (ok,  fail)
print run_cmd(hi, ':quit ')

