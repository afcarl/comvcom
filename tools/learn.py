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

    def __init__(self, name):
        self.name = name
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
            v = e[self.name]
            if v in d:
                d[v].append(e)
            else:
                d[v] = [e]
        if len(d) < 2: raise self.InvalidSplit
        n = len(ents)
        avgetp = sum( len(es) * entetp(es) for es in d.values() ) / n
        split = list(d.values())
        return (avgetp, None, split)
DF = DiscreteFeature

##  QuantitativeFeature
##
class QuantitativeFeature(Feature):

    def split(self, ents):
        assert 2 <= len(ents)
        pairs = [ (e, e[self.name]) for e in ents ]
        pairs.sort(key=(lambda ev: ev[1]))
        es = [ e for (e,_) in pairs ]
        vs = [ v for (_,v) in pairs ]
        n = len(ents)
        minsplit = minetp = None
        v0 = vs[0]
        for i in range(1, n):
            v1 = vs[i]
            if v0 == v1: continue
            v0 = v1
            avgetp = (i * entetp(es[:i]) + (n-i) * entetp(es[i:])) / n
            if minsplit is None or avgetp < minetp:
                minetp = avgetp
                minsplit = i
        if minsplit is None: raise self.InvalidSplit
        arg = ('<', vs[minsplit])
        split = [es[:minsplit], es[minsplit:]]
        return (minetp, arg, split)
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

    def __init__(self, features, minkeys=2, minent=0.01, debug=1):
        self.features = features
        self.minkeys = minkeys
        self.minent = minent
        self.debug = debug
        return

    def build(self, ents, depth=0):
        keys = countkeys(ents)
        etp = getetp(keys)
        if self.debug:
            print ('Build:', keys, etp)
        if len(ents) < 2: return None
        if len(keys) < self.minkeys: return None
        if etp < self.minent: return None
        minbranch = minetp = None
        for feat in self.features:
            try:
                (etp, arg, split) = feat.split(ents)
            except Feature.InvalidSplit:
                continue
            if minbranch is None or etp < minetp:
                minetp = etp
                minbranch = (feat, arg, split)
        if minbranch is None: return None
        (feat, arg, split) = minbranch
        if self.debug:
            print ('Feature:', feat, arg, etp)
            for (i,ents) in enumerate(split):
                r = [ (e[feat.name], e.key) for e in ents ]
                print (' Split%d (%d): %r' % (i, len(r), r))
        children = []
        for es in split:
            branch = self.build(es, depth+1)
            if branch is not None:
                children.append(branch)
        return TreeBranch(feat, arg, children)


# main
def main(argv):
    import fileinput
    args = argv[1:]
    fp = fileinput.input(args)
    ents = []
    for e in CommentEntry.load(fp):
        e.key = e['key'][0]
        e['deltaLine'] = int(e['line']) - int(e.get('prevLine',0))
        e['deltaCols'] = int(e['cols']) - int(e.get('prevCols',0))
        ents.append(e)
    builder = TreeBuilder([QF('deltaLine'), QF('deltaCols')])
    root = builder.build(ents)
    root.dump()
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
