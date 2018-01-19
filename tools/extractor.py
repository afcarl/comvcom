#!/usr/bin/env python
import sys
import ast
import tokenize

class Source:

    def __init__(self):
        self.lines = []
        self.text = ''
        return

    def load(self, fp):
        for line in fp:
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
        return tokenize.generate_tokens(readline)

    def parse(self):
        return ast.parse(self.text)

def doit(path):
    src = Source()
    with open(path) as fp:
        src.load(fp)
    tokenlen = {}
    comments = []
    for (t,s,start,end,line) in src.tokenize():
        i0 = src.getindex(start)
        i1 = src.getindex(end)
        tokenlen[i0] = (i1-i0)
        if t == tokenize.COMMENT:
            comments.append((i0, i1))
    ends = {}
    def getend(node):
        if node in ends:
            end = ends[node]
        else:
            end = 0
            if isinstance(node, ast.expr) or isinstance(node, ast.stmt):
                loc = (node.lineno, node.col_offset)
                index = src.getindex(loc)
                end = max(end, index+tokenlen.get(index))
            for c in ast.iter_child_nodes(node):
                end = max(end, getend(c))
            ends[node] = end
        return end
    spans = []
    def walk(node):
        if isinstance(node, ast.expr) or isinstance(node, ast.stmt):
            name = type(node).__name__
            loc = (node.lineno, node.col_offset)
            start = src.getindex(loc)
            end = getend(node)
            spans.append((start, end, name))
        for c in ast.iter_child_nodes(node):
            walk(c)
        return
    tree = src.parse()
    walk(tree)
    print(spans)
    return

def main(argv):
    args = argv[1:]
    for path in args:
        doit(path)
    return
if __name__ == '__main__': sys.exit(main(sys.argv))
