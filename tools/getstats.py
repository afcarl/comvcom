#!/usr/bin/env python
import sys
import os.path
from comment import CommentEntry

def main(argv):
    args = argv[1:]
    for path in args:
        sys.stderr.write(path+'...\n'); sys.stderr.flush()
        name = os.path.basename(path)
        (name,_) = os.path.splitext(name)
        (name,_,_) = name.rpartition('-')
        cc = {}
        with open(path) as fp:
            for e in CommentEntry.load(fp):
                cat = e['predCategory']
                cc[cat] = cc.get(cat, 0)+1
        total = sum(cc.values())
        a = sorted(cc.items(), key=lambda x:x[1], reverse=True)
        print ('+', name, total, ' '.join( '%s:%d(%.2f)' % (c,n,n/total) for (c,n) in a ))
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
