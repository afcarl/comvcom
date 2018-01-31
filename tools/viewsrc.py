#!/usr/bin/env python
import sys
from comment import CommentEntry
from srcdb import SourceDB

def main(argv):
    import fileinput
    import getopt
    def usage():
        print('usage: %s [-c context] [-f k=v] basedir out.comm' %
              argv[0])
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'c:f:')
    except getopt.GetoptError:
        return usage()
    ncontext = 4
    filters = []
    for (k, v) in opts:
        if k == '-c': ncontext = int(v)
        elif k == '-f':
            (a,_,b) = v.partition('=')
            filters.append((a,b))
    if not args: return usage()

    path = args.pop(0)
    srcdb = SourceDB(path)

    fp = fileinput.input(args)
    for e in CommentEntry.load(fp):
        for (k,v) in filters:
            if e[k] != v: break
        else:
            src = srcdb.get(e.path)
            print('@ %s %r' % (src.name, e.spans))
            ranges = [(s,e,True) for (s,e) in e.spans]
            for (_,line) in src.show(ranges, ncontext=ncontext):
                print('  '+line, end='')
            print()
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
