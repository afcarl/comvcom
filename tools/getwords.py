#!/usr/bin/env python
import sys
from comment import CommentEntry

POS1 = frozenset('VB VBZ VBP VBD VBN VBG'.split(' '))
POS2 = frozenset('NN NNS NNP NNPS'.split(' '))
NTOP = 100

def getwords(fp):
    wc = {}
    for e in CommentEntry.load(fp):
        cat = e['predCategory']
        if cat != 'p': continue
        if 'words' not in e or 'posTags' not in e: continue
        words = e['words'].split(',')
        postags = e['posTags'].split(',')
        pairs = list(zip(words, postags))
        for (i,(w1,p1)) in enumerate(pairs):
            if p1 not in POS1: continue
            for (w2,p2) in pairs[i+1:]:
                if p2 not in POS2: continue
                k = (w1,w2)
                wc[k] = wc.get(k, 0)+1
    return wc

def main(argv):
    args = argv[1:]
    gwc = {}
    for path in args:
        sys.stderr.write(path+'...\n'); sys.stderr.flush()
        with open(path) as fp:
            wc = getwords(fp)
        for k in wc.keys():
            gwc[k] = gwc.get(k, 0)+1
    a = sorted(gwc.items(), key=lambda x:x[1], reverse=True)
    for (k,n) in a[:NTOP]:
        print('#', ' '.join(k), n)
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
