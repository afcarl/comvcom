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

class Source:

    def __init__(self):
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
                end = max(end, index+self.toklen.get(index))
            for c in ast.iter_child_nodes(node):
                end = max(end, self.getend(c))
            self.nodeend[node] = end
        return end

    def parse(self):
        tree = ast.parse(self.text)
        node_start = {}
        node_end = {}
        def walk(node):
            if isinstance(node, ast.expr) or isinstance(node, ast.stmt):
                name = type(node).__name__
                loc = (node.lineno, node.col_offset)
                start = self.getindex(loc)
                self.nodestart[node] = start
                end = self.getend(node)
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


def extract(path):
    src = Source()
    with open(path) as fp:
        src.load(fp)
    src.tokenize()
    src.parse()
    comments = []
    for (t,start,end) in src.tokens:
        if t == tokenize.COMMENT:
            comments.append((start, end))
    for (start,end) in comments:
        feats = {}
        ent = CommentEntry(path, start+1, end, feats)
        yield ent
    return

def main(argv):
    args = argv[1:]
    for path in args:
        for ent in extract(path):
            print (ent)
    return
if __name__ == '__main__': sys.exit(main(sys.argv))
