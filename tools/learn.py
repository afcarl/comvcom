#!/usr/bin/env python
##
##  learn.py
##
##  Usage:
##    $ learn.py comments.feats
##
import sys
from math import log
from comment import CommentEntry

def getetp(ents):
    n = len(ents)
    d = {}
    for ent in ents:
        k = ent.key
        if k in d:
            d[k] += 1
        else:
            d[k] = 1
    etp = sum( v*log(n/v) for v in d.values() ) / n
    return etp

class Selector:

    def __init__(self, name, func):
        self.name = name
        self.func = func
        return

    def __repr__(self):
        return ('<%s: %s>' % (self.__class__.__name__, self.name))

    def split(self, ents):
        raise NotImplementedError

class Branch:

    def __init__(self, selector, arg, etp, splits):
        self.selector = selector
        self.arg = arg
        self.etp = etp
        self.splits = splits
        return

    def __repr__(self):
        return ('<Branch(%r, %r): etp=%.2f, %r>' %
                (self.selector, self.arg, self.etp,
                 [ len(a) for a in  self.splits ]))

class DS(Selector):

    def split(self, ents):
        if len(ents) <= 1: return None
        d = {}
        for e in ents:
            v = self.func(e)
            if v in d:
                d[v].append(e)
            else:
                d[v] = [e]
        n = len(ents)
        avgetp = sum( len(a) * getetp(a) for a in d.values() ) / n
        return Branch(self, None, avgetp, list(d.values()))

class QS(Selector):

    def split(self, ents):
        if len(ents) <= 2: return None
        a = sorted(ents, key=(lambda e: self.func(e)))
        n = len(ents)
        minsplit = minetp = None
        for i in range(1, n-1):
            avgetp = (i * getetp(a[:i]) + (n-i) * getetp(a[i:])) / n
            if minsplit is None or avgetp < minetp:
                minetp = avgetp
                minsplit = i
        assert minsplit is not None
        threshold = self.func(a[minsplit])
        arg = '<%r' % threshold
        return Branch(self, arg, minetp, [a[:minsplit], a[minsplit:]])

class TreeBuilder:

    def __init__(self, selectors):
        self.selectors = selectors
        return

    def build(self, ents, depth=0, minetp=sys.maxsize):
        branch0 = None
        for selector in self.selectors:
            branch1 = selector.split(ents)
            if branch1 is not None and branch1.etp < minetp:
                minetp = branch1.etp
                branch0 = branch1
        if branch0 is None: return
        print ('branch', depth, branch0)
        for split in branch0.splits:
            self.build(split, depth+1, branch0.etp)
        return

builder1 = TreeBuilder([
    QS('deltaLine', (lambda e: int(e['line']) - int(e.get('prevLine',0)))),
    QS('deltaCols', (lambda e: int(e['cols']) - int(e.get('prevCols',0)))),
])

def main(argv):
    import fileinput
    args = argv[1:]
    fp = fileinput.input(args)
    ents = []
    for ent in CommentEntry.load(fp):
        ent.key = ent['key'][0]
        ents.append(ent)
    builder1.build(ents)
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
