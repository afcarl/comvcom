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
from srcdb import SourceDB


def calcetp(keys):
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

def bestkey(keys):
    maxkey = None
    maxv = 0
    for (k,v) in keys.items():
        if maxkey is None or maxv < v:
            maxkey = k
            maxv = v
    assert maxkey is not None
    return maxkey

def entetp(ents):
    return calcetp(countkeys(ents))


##  Feature
##
class Feature:

    class InvalidSplit(ValueError): pass

    def __init__(self, name):
        self.name = name
        return

    def __repr__(self):
        return ('<%s: %s>' % (self.__class__.__name__, self.name))

    def get(self, e):
        return e[self.name]

    def split(self, ents):
        raise NotImplementedError

    def ident(self, arg, e):
        raise NotImplementedError

##  DiscreteFeature
##
class DiscreteFeature(Feature):

    def ident(self, arg, e):
        return self.get(e)

    def split(self, ents):
        assert 2 <= len(ents)
        d = {}
        for e in ents:
            v = self.get(e)
            if v in d:
                d[v].append(e)
            else:
                d[v] = [e]
        if len(d) < 2: raise self.InvalidSplit
        n = len(ents)
        avgetp = sum( len(es) * entetp(es) for es in d.values() ) / n
        split = list(d.items())
        return (avgetp, None, split)

DF = DiscreteFeature

##  QuantitativeFeature
##
class QuantitativeFeature(Feature):

    def get(self, e):
        return e[self.name]

    def ident(self, arg, e):
        v = self.get(e)
        if v < arg:
            return 'lt'
        else:
            return 'ge'

    def split(self, ents):
        assert 2 <= len(ents)
        pairs = [ (e, self.get(e)) for e in ents ]
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
        arg = vs[minsplit]
        split = [('lt', es[:minsplit]), ('ge', es[minsplit:])]
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

    def run(self, e):
        v0 =  self.feature.ident(self.arg, e)
        for (v,branch) in self.children:
            if v == v0: break
        return branch.run(e)

    def dump(self, depth=0):
        ind = '  '*depth
        print ('%sBranch %r: %r' % (ind, self.feature, self.arg))
        for (v,branch) in self.children:
            print ('%s Value: %r' % (ind, v))
            branch.dump(depth+1)
        return

##  TreeLeaf
##
class TreeLeaf:

    def __init__(self, key):
        self.key = key
        return

    def __repr__(self):
        return ('<TreeLeaf(%r)>' % (self.key))

    def run(self, e):
        return self.key

    def dump(self, depth=0):
        ind = '  '*depth
        print ('%sLeaf %r' % (ind, self.key))
        return


##  TreeBuilder
##
class TreeBuilder:

    FEATURES = (
        DF('type'),
        QF('deltaLine'),
        QF('deltaCols'),
    )

    name2feat = { feat.name: feat for feat in FEATURES }

    def __init__(self, names, minkeys=2, minent=0.01, debug=1):
        self.features = [ self.getfeat(name) for name in names ]
        self.minkeys = minkeys
        self.minent = minent
        self.debug = debug
        return

    @classmethod
    def getfeat(klass, name):
        return klass.name2feat[name]

    def build(self, ents, depth=0):
        keys = countkeys(ents)
        etp = calcetp(keys)
        ind = '  '*depth
        if self.debug:
            print ('%sBuild: %r, etp=%.3f' % (ind, keys, etp))
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
            print ('%sFeature: %r, arg=%r, etp=%.3f' % (ind, feat, arg, etp))
        children = []
        for (i,(v,es)) in enumerate(split):
            if 2 <= self.debug:
                r = [ (e[feat.name], e.key) for e in es ]
                print ('%s Split%d (%d): %r, %r' % (ind, i, len(r), v, r))
            branch = self.build(es, depth+1)
            if branch is None:
                keys = countkeys(es)
                if self.debug:
                    print ('%s Leaf: %r' % (ind, keys))
                branch = TreeLeaf(bestkey(keys))
            children.append((v, branch))
        return TreeBranch(feat, arg, children)


# export_tree
def export_tree(tree):
    if isinstance(tree, TreeBranch):
        children = [ (v,export_tree(branch)) for (v,branch) in tree.children ]
        return (tree.feature.name, tree.arg, children)
    else:
        return (tree.key)

# import_tree
def import_tree(builder, tree):
    if isinstance(tree, tuple):
        (name, arg, children) = tree
        children = [ (v,import_tree(builder, branch)) for (v,branch) in children ]
        return TreeBranch(builder.getfeat(name), arg, children)
    else:
        return TreeLeaf(tree)


# main
def main(argv):
    import getopt
    import fileinput
    def usage():
        print('usage: %s [-d] [-f feats] [file ...]' % argv[0])
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'dB:f:')
    except getopt.GetoptError:
        return usage()
    debug = 0
    srcdb = None
    feats = None
    for (k, v) in opts:
        if k == '-d': debug += 1
        elif k == '-B': srcdb = SourceDB(v)
        elif k == '-f': feats = v
    fp = fileinput.input(args)
    ents = []
    for e in CommentEntry.load(fp):
        e.key = e['key'][0]
        e['deltaLine'] = int(e['line']) - int(e.get('prevLine',0))
        e['deltaCols'] = int(e['cols']) - int(e.get('prevCols',0))
        ents.append(e)
    builder = TreeBuilder(['type', 'deltaLine', 'deltaCols'], debug=debug)
    if feats is None:
        # learning
        root = builder.build(ents)
        if debug:
            root.dump()
        print (export_tree(root))
    else:
        with open(feats) as fp:
            data = eval(fp.read())
        tree = import_tree(builder, data)
        correct = 0
        for e in ents:
            key = tree.run(e)
            if e.key == key:
                correct += 1
            elif srcdb is not None:
                print(e)
                src = srcdb.get(e.path)
                for (_,line) in src.show([(e.start, e.end, 1)]):
                    print(line, end='')
        print (correct, len(ents))
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
