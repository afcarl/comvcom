#!/usr/bin/env python
import sys
import ast
import tokenize
from comment import CommentEntry

def bisect_right(a, x):
    lo = 0
    hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        (k,_) = a[mid]
        if x < k: hi = mid
        else: lo = mid+1
    return lo

def bisect_left(a, x):
    lo = 0
    hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        (k,_) = a[mid]
        if k < x: lo = mid+1
        else: hi = mid
    return lo

def nodename(node):
    return type(node).__name__

def bl(x):
    if x:
        return 'true'
    else:
        return 'false'

class Source:

    def __init__(self, tab=8):
        self.tab = tab
        self.lines = []
        self.text = ''
        self.tokens = []
        self.toklen = {}
        self.nodestart = {}
        self.nodeend = {}
        self.parent = {}
        self.node_start = []
        self.node_end = []
        return

    def load(self, fp):
        for line in fp:
            if u'' is not '':
                line = line.decode('utf-8')
            line = line.replace(u'\ufeff',u'').replace(u'\ufffe',u'').replace('\r','')
            self.lines.append((len(self.text), line))
            self.text += line
        self.lines.append((len(self.text), ''))
        return

    def get(self, start, end):
        return self.text[start:end]

    def getindex(self, loc):
        (row,col) = loc
        (index,_) = self.lines[row-1]
        return (index+col)

    def getrow(self, index):
        return bisect_right(self.lines, index)-1

    def getcol(self, index):
        lineno = bisect_right(self.lines, index)-1
        (i0,_) = self.lines[lineno]
        col = 0
        for c in self.text[i0:index]:
            if c == '\t':
                col = ((col//self.tab)+1)*self.tab
            else:
                col += 1
        return col

    def tokenize(self):
        self._i = 0
        def readline():
            if self._i < len(self.lines):
                (_,line) = self.lines[self._i]
                self._i += 1
                return line
            else:
                return ''
        for (t,s,start,end,line) in tokenize.generate_tokens(readline):
            i0 = self.getindex(start)
            i1 = self.getindex(end)
            self.toklen[i0] = (i1-i0)
            self.tokens.append((t, i0, i1))
        return

    def getlen(self, node):
        return self.getend(node) - self.nodestart[node]

    def getstart(self, node):
        return self.nodestart[node]

    def getend(self, node):
        if node in self.nodeend:
            end = self.nodeend[node]
        else:
            end = 0
            if isinstance(node, ast.expr) or isinstance(node, ast.stmt):
                loc = (node.lineno, node.col_offset)
                index = self.getindex(loc)
                end = max(end, index+self.toklen.get(index, 0))
            for c in ast.iter_child_nodes(node):
                end = max(end, self.getend(c))
            self.nodeend[node] = end
        return end

    def getparents(self, node):
        nodes = []
        while node is not None:
            nodes.append(node)
            node = self.parent.get(node)
        return nodes

    def parse(self):
        tree = ast.parse(self.text)
        node_start = {}
        node_end = {}
        def add(node, start, end):
            self.nodestart[node] = start
            if start in node_start:
                a = node_start[start]
            else:
                a = node_start[start] = []
            a.append(node)
            if end in node_end:
                a = node_end[end]
            else:
                a = node_end[end] = []
            a.append(node)
            return
        def walk(node):
            if isinstance(node, ast.Module):
                start = 0
                end = len(self.text)
                add(node, start, end)
            elif isinstance(node, ast.expr) or isinstance(node, ast.stmt):
                loc = (node.lineno, node.col_offset)
                start = self.getindex(loc)
                end = self.getend(node)
                add(node, start, end)
            for c in ast.iter_child_nodes(node):
                self.parent[c] = node
                walk(c)
            return
        walk(tree)
        for (pos,nodes) in node_start.items():
            nodes.sort(key=self.getlen, reverse=True)
            self.node_start.append((pos, nodes))
        self.node_start.sort(key=lambda x:x[0])
        for (pos,nodes) in node_end.items():
            nodes.sort(key=self.getlen, reverse=True)
            self.node_end.append((pos, nodes))
        self.node_end.sort(key=lambda x:x[0])
        return

    def getNodesStartAfter(self, pos):
        i = bisect_left(self.node_start, pos)
        if i == len(self.node_start): return []
        (_,nodes) = self.node_start[i]
        return nodes

    def getNodesEndBefore(self, pos):
        i = bisect_right(self.node_end, pos)
        if i == 0: return []
        (_,nodes) = self.node_end[i-1]
        return nodes

    def getNodesOutside(self, start, end):
        i0 = bisect_left(self.node_start, start)
        i1 = bisect_right(self.node_end, end)
        a = set()
        for (_,nodes) in self.node_start[:i0]:
            a.update(nodes)
        b = set()
        for (_,nodes) in self.node_end[i1:]:
            b.update(nodes)
        c = list(a.intersection(b))
        c.sort(key=self.getlen)
        return c

# getfeats
def getfeats(src):
    for (t,start,end) in src.tokens:
        if t != tokenize.COMMENT: continue
        feats = {'type':'LineComment'}
        feats['line'] = src.getrow(start)
        feats['cols'] = src.getcol(start)
        before = src.getNodesEndBefore(start)
        if before:
            feats['leftTypes'] = ','.join( nodename(n) for n in before )
            feats['leftLine'] = src.getrow(src.getend(before[0]))
        after = src.getNodesStartAfter(end)
        if after:
            feats['rightTypes'] = ','.join( nodename(n) for n in after )
            feats['rightLine'] = src.getrow(src.getend(after[0]))
        parent = None
        for n in src.getNodesOutside(start, end):
            if parent is None or src.getlen(n) < src.getlen(parent):
                parent = n
        if parent is not None:
            parents = src.getparents(parent)
            feats['parentTypes'] = ','.join( nodename(n) for n in parents )
            pstart = src.getstart(parent)
            pend = src.getend(parent)
            feats['parentStart'] = bl(pstart == start)
            feats['parentEnd'] = bl(pend == end)
        yield (start, end, feats)
    return

def main(argv):
    import getopt
    def usage():
        print('usage: %s [-d] [-t tab] [file ...]' % argv[0])
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'dt:')
    except getopt.GetoptError:
        return usage()
    debug = 0
    tab = 8
    for (k, v) in opts:
        if k == '-d': debug += 1
        elif k == '-t': tab = int(v)
    for path in args:
        src = Source(tab=tab)
        with open(path) as fp:
            src.load(fp)
        try:
            src.tokenize()
            src.parse()
        except SyntaxError as e:
            print('!', path)
            continue
        prev = None
        for (start,end,feats) in getfeats(src):
            if prev is not None:
                (start0,end0) = prev
                feats['prevLine'] = src.getrow(end0)
                feats['prevCols'] = src.getcol(start0)
            prev = (start,end)
            ent = CommentEntry(path, start+1, end, feats)
            print(ent)
            s = src.get(start+1, end).replace('\n',' ')
            print('+ %s\n' % s)
    return
if __name__ == '__main__': sys.exit(main(sys.argv))
