#!/usr/bin/env python
import sys
from comment import CommentEntry
from learncomm import TreeBuilder
from learncomm import add_comm_feats
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
    add_comm_feats(builder)

    path = args.pop(0)
    with open(path) as fp:
        data = eval(fp.read())
    tree = builder.import_tree(data)

    correct = {}
    keys = {}
    resp = {}
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
        if 'MethodDeclaration' not in e['parentTypes'].split(','): continue
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

        key = e[keyprop]
        cat = tree.test(e)
        e[resprop] = cat
        if key is not None and key != 'u':
            keys[key] = keys.get(key,0)+1
            resp[cat] = resp.get(cat,0)+1
            if key == cat:
                correct[cat] = correct.get(cat,0)+1
        print(e)
        if srcdb is not None:
            src = srcdb.get(e.path)
            ranges = [(s,e,1) for (s,e) in e.spans]
            for (_,line) in src.show(ranges):
                print(line, end='')
            print()
    #
    if debug:
        for (k,v) in correct.items():
            p = v/resp[k]
            r = v/keys[k]
            f = 2*(p*r)/(p+r)
            print ('%s: prec=%.3f(%d/%d), recl=%.3f(%d/%d), F=%.3f' %
                   (k, p, v, resp[k], r, v, keys[k], f))
        print ('%d/%d' % (sum(correct.values()), sum(keys.values())))
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
