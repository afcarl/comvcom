#!/usr/bin/env python
import sys
from comment import CommentEntry
from srcdb import SourceDB

def show(cid, src, spans, key, ncontext=4):
    ranges = [(s,e,True) for (s,e) in spans]
    print('# %s:' % cid)
    print('@ %s %r key=%s' % (src.name, spans, key))
    for (_,line) in src.show(ranges, ncontext=ncontext):
        print('  '+line, end='')
    print()
    return

def main(argv):
    import fileinput
    import getopt
    def usage():
        print('usage: %s [-B basedir] [-c context] out.comm' %
              argv[0])
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'B:c:')
    except getopt.GetoptError:
        return usage()
    srcdb = None
    ncontext = 4
    for (k, v) in opts:
        if k == '-B': srcdb = SourceDB(v)
        elif k == '-c': ncontext = int(v)
    if not args: return usage()

    fp = fileinput.input(args)
    index = 0
    for e in CommentEntry.load(fp):
        src = srcdb.get(e.path)
        cid = 'c%03d' % index
        show(cid, src, e.spans, e.key, ncontext=ncontext)
        index += 1
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
