#!/usr/bin/env python
import sys
from comment import CommentEntry
from learncomm import TreeBuilder
from learncomm import add_cat_feats
from srcdb import SourceDB

MAP = {
    'Name': ('SimpleName',),
    'FunctionDef': ('Block','MethodDeclaration'),
    'Module': ('CompilationUnit',),
    'Assign': ('ExpressionStatement',),
    'ClassDef': ('TypeDeclaration',),
    'If': ('Block','IfStatement'),
    'Call': ('MethodInvocation',),
    'Expr': ('ExpressionStatement',),
    'Attribute': ('QualifiedName',),
    'For': ('Block','ForStatement',),
    'TryExcept': ('Block','TryStatement',),
    'Return': ('ReturnStatement',),
    'Str': ('StringLiteral',),
    'Num': ('NumberLiteral',),
    'With': ('Block','TryStatement',),
    'While': ('Block','WhileStatement',),
    'Tuple': ('ArrayInitializer',),
    'List': ('ArrayInitializer',),
    'Compare': ('InfixExpression',),
    'Subscript': ('ArrayAccess',),
    'Raise': ('ThrowStatement',),
    'ListComp': ('ArrayInitializer',),
    'Dict': ('ArrayInitializer',),
    'Continue': ('ContinueStatement',),
    'BoolOp': ('InfixExpression',),
    'BinOp': ('InfixExpression',),
    'AugAssign': ('Assignment',),
    'Yield': ('ReturnStatement',),
    'UnaryOp': ('PrefixExpression',),
    'TryFinally': ('Block','TryStatement',),
    'Pass': ('BreakStatement',),
}
def pythonify(v0):
    a = []
    for x in v0.split(','):
        a.extend(MAP.get(x,x))
    v1 = ','.join(a)
    #print (v0, v1)
    return v1

def Z(x): return max(1, x)

def main(argv):
    import getopt
    import fileinput
    def usage():
        print('usage: %s [-d] [-P] [-B srcdb] [-k keyprop] [-r resprop] [file ...]' %
              argv[0])
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'dPB:k:r:')
    except getopt.GetoptError:
        return usage()
    debug = 0
    pythonmode = False
    srcdb = None
    keyprop = 'keyCategory'
    resprop = 'predCategory'
    for (k, v) in opts:
        if k == '-d': debug += 1
        elif k == '-P': pythonmode = True
        elif k == '-B': srcdb = SourceDB(v)
        elif k == '-k': keyprop = v
        elif k == '-r': resprop = v
    builder = TreeBuilder()
    add_cat_feats(builder)

    path = args.pop(0)
    with open(path) as fp:
        data = eval(fp.read())
    tree = builder.import_tree(data)

    mat = {}
    keys = set()
    fp = fileinput.input(args)
    for e in CommentEntry.load(fp):
        if 'parentTypes' not in e: continue
        if pythonmode:
            e['parentTypes'] = pythonify(e['parentTypes'])
            if 'leftTypes' in e:
                e['leftTypes'] = pythonify(e['leftTypes'])
            if 'rightTypes' in e:
                e['rightTypes'] = pythonify(e['rightTypes'])
        # ignore non-local comments.
        if 'Block,MethodDeclaration' not in e['parentTypes']: continue
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

        cat0 = e[keyprop]
        assert cat0, e
        keys.add(cat0)
        cat1 = tree.test(e)
        keys.add(cat1)
        e[resprop] = cat1
        if cat0 is not None and cat0 != 'u':
            k = (cat0,cat1)
            mat[k] = mat.get(k, 0)+1
        print(e)
        if srcdb is not None:
            src = srcdb.get(e.path)
            ranges = [(s,e,1) for (s,e) in e.spans]
            for (_,line) in src.show(ranges):
                print(line, end='')
            print()
    #
    if debug:
        #keys = sorted(keys)
        keys = ('p','a','c','v','o','d','i')
        print ('A\C  %s| recall' % ('|'.join( '%5s' % k for k in keys )))
        col_t = {}
        row_t = {}
        for cat0 in keys:
            a = {}
            for cat1 in keys:
                v = mat.get((cat0,cat1), 0)
                a[cat1] = v
                col_t[cat1] = col_t.get(cat1, 0)+v
            row_c = mat.get((cat0,cat0), 0)
            row_t1 = sum(a.values())
            row_t[cat0] = row_t1
            print ('%4s:%s| %.3f(%2d/%2d)' %
                   (cat0, '|'.join( '%5d' % a[cat1] for cat1 in keys ),
                    row_c/Z(row_t1), row_c, row_t1))
        print ('prec.%s' %
               ('|'.join( '%2d/%2d' % (mat.get((cat,cat), 0), col_t[cat])
                          for cat in keys )))
        print ('     %s' %
               ('|'.join( '%2.3f' % (mat.get((cat,cat), 0)/Z(col_t[cat]))
                          for cat in keys )))
        print()
        for cat in keys:
            v = mat.get((cat,cat), 0)
            p = v/Z(col_t[cat])
            r = v/Z(row_t[cat])
            f = 2*(p*r)/Z(p+r)
            print ('%s: prec=%.3f(%d/%d), recl=%.3f(%d/%d), F=%.3f' %
                   (cat, p, v, col_t[cat], r, v, row_t[cat], f))
        print ('%d/%d' % (sum( v for ((cat0,cat1),v) in mat.items() if cat0 == cat1 ),
                          sum(mat.values())))
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
