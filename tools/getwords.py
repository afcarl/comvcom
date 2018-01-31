#!/usr/bin/env python
import sys
from comment import CommentEntry

POS_IGNORED = ('DT','IN','TO','PDT','SYM')
NTOP = 100

def getstat(fp, wc):
    for e in CommentEntry.load(fp):
        cat = e['predCategory']
        if cat != 'p': continue
        if 'words' not in e or 'posTags' not in e: continue
        words = e['words'].split(',')
        postags = e['posTags'].split(',')
        pairs = list(zip(words, postags))
        for (i,(w1,p1)) in enumerate(pairs):
            if p1 in POS_IGNORED: continue
            for (w2,p2) in pairs[i+1:]:
                if p2 in POS_IGNORED: continue
                k = (w1,w2)
                wc[k] = wc.get(k, 0)+1
    return

def main(argv):
    args = argv[1:]
    wc = {}
    for path in args:
        sys.stderr.write(path+'...\n'); sys.stderr.flush()
        with open(path) as fp:
            getstat(fp, wc)
    a = sorted(wc.items(), key=lambda x:x[1], reverse=True)
    for (k,n) in a[:NTOP]:
        print('#', ' '.join(k), n)
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
