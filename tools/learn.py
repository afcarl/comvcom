#!/usr/bin/env python
##
##  learn.py
##
##  Usage:
##    $ learn.py comments.feats
##
import sys
from math import log2
from comment import CommentEntry

# getetp: calc the entropy.
def getetp(keys):
    n = sum(keys.values())
    etp = sum( v*log2(n/v) for v in keys.values() ) / n
    return etp

def countkeys(ents):
    d = {}
    for e in ents:
        k = e.key
        if k in d:
            d[k] += 1
        else:
            d[k] = 1
    return d

def entetp(ents):
    return getetp(countkeys(ents))


##  Feature
##
class Feature:

    class InvalidSplit(ValueError): pass

    def __init__(self, name, func):
        self.name = name
        self.func = func
        return

    def __repr__(self):
        return ('<%s: %s>' % (self.__class__.__name__, self.name))

    def split(self, ents):
        raise NotImplementedError

##  DiscreteFeature
##
class DiscreteFeature(Feature):

    def split(self, ents):
        assert 2 <= len(ents)
        d = {}
        for e in ents:
            v = self.func(e)
            if v in d:
                d[v].append(e)
            else:
                d[v] = [e]
        n = len(ents)
        avgetp = sum( len(es) * entetp(es) for es in d.values() ) / n
        return (avgetp, None, list(d.values()))
DF = DiscreteFeature

##  QuantitativeFeature
##
class QuantitativeFeature(Feature):

    def split(self, ents):
        assert 2 <= len(ents)
        es = sorted(ents, key=(lambda e: self.func(e)))
        n = len(ents)
        minsplit = minetp = None
        for i in range(1, n-1):
            avgetp = (i * entetp(es[:i]) + (n-i) * entetp(es[i:])) / n
            if minsplit is None or avgetp < minetp:
                minetp = avgetp
                minsplit = i
        assert minsplit is not None
        threshold = self.func(es[minsplit])
        arg = '<%r' % threshold
        return (minetp, arg, [es[:minsplit], es[minsplit:]])
QF = QuantitativeFeature


##  TreeBranch
##
class TreeBranch:

    def __init__(self, feature, arg, children):
        self.feature = feature
        self.arg = arg
        self.children = children
        return

    def __repr__(self):
        return ('<TreeBranch(%r, %r)>' %
                (self.feature, self.arg))

    def dump(self, depth=0):
        ind = ' '*depth
        print ('%sBranch %r: %r' % (ind, self.feature, self.arg))
        for branch in self.children:
            branch.dump(depth+1)
        return


##  TreeBuilder
##
class TreeBuilder:

    def __init__(self, features, minkeys=2, minent=0.01):
        self.features = features
        self.minkeys = minkeys
        self.minent = minent
        return

    def build(self, ents, depth=0):
        if len(ents) < 2: return None
        keys = countkeys(ents)
        if len(keys) < self.minkeys: return None
        if getetp(keys) < self.minent: return None
        minbranch = minetp = None
        for feature in self.features:
            try:
                (etp, arg, split) = feature.split(ents)
            except Feature.InvalidSplit:
                continue
            if minbranch is None or etp < minetp:
                minetp = etp
                minbranch = (feature, arg, split)
        if minbranch is None: return None
        (feature, arg, split) = minbranch
        print ('branch', depth, feature, arg)
        children = []
        for ents in split:
            branch = self.build(ents, depth+1)
            if branch is not None:
                children.append(branch)
        return TreeBranch(feature, arg, children)

builder1 = TreeBuilder([
    QF('deltaLine', (lambda e: int(e['line']) - int(e.get('prevLine',0)))),
    QF('deltaCols', (lambda e: int(e['cols']) - int(e.get('prevCols',0)))),
])

def main(argv):
    import fileinput
    args = argv[1:]
    fp = fileinput.input(args)
    ents = []
    for ent in CommentEntry.load(fp):
        ent.key = ent['key'][0]
        ents.append(ent)
    root = builder1.build(ents)
    root.dump()
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
