#!/usr/bin/env python
import sys
from comment import CommentEntry
from srcdb import SourceDB
from learncomm import TreeBuilder

def main(argv):
    import fileinput
    builder = TreeBuilder()
    builder.addfeat('QF:deltaLine')
    builder.addfeat('QF:deltaCols')
    builder.addfeat('QF:deltaLeft')
    builder.addfeat('QF:deltaRight')
    builder.addfeat('DF:type')
    builder.addfeat('DF:parentStart')
    builder.addfeat('DF:parentEnd')

    args = argv[1:]
    path = args.pop(0)
    with open(path) as fp:
        data = eval(fp.read())
    tree = builder.import_tree(data)

    def merge(ents):
        e0 = ents.pop(0)
        for e1 in ents:
            e0.merge(e1)
            if 'rightLine' in e1:
                e0['rightLine'] = e1['rightLine']
            if 'rightTypes' in e1:
                e0['rightTypes'] = e1['rightTypes']
            if 'deltaRight' in e1:
                e0['deltaRight'] = e1['deltaRight']
        return e0

    fp = fileinput.input(args)
    b = []
    prev = None
    for e in CommentEntry.load(fp):
        line = int(e['line'])
        cols = int(e['cols'])
        if 'prevLine' in e:
            e['deltaLine'] = line - int(e['prevLine'])
        if 'prevCols' in e:
            e['deltaCols'] = cols - int(e['prevCols'])
        if 'leftLine' in e:
            e['deltaLeft'] = line - int(e['leftLine'])
        if 'rightLine' in e:
            e['deltaRight'] = line - int(e['rightLine'])
        if prev is not None:
            if (prev.path != e.path or
                prev['type'] != e['type'] or
                prev['parentTypes'] != e['parentTypes']):
                if b:
                    print(merge(b))
                    b = []
        try:
            bio = tree.test(e)
        except ValueError:
            bio = 'B'
        e['keyBIO'] = bio
        if bio == 'B':
            if b:
                print(merge(b))
                b = []
        b.append(e)
        prev = e
    if b:
        print(merge(b))
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
