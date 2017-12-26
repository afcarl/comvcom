#!/usr/bin/env python
import sys

class CommentEntry:

    def __init__(self, path, start, end, feats, key=None):
        self.path = path
        self.start = start
        self.end = end
        self.feats = feats
        self.key = key
        return

    def __repr__(self):
        return ('<%s: path=%r, start=%r, end=%r, feats=%r>' %
                (self.__class__.__name__,
                 self.path, self.start, self.end, self.feats))

    def __str__(self):
        feats = ' '.join( '%s=%s' % (k,v) for (k,v) in self.feats.items() )
        return ('@ %s %d %d %s' %
                (self.path, self.start, self.end, feats))

    def merge(self, entry):
        assert self.path == entry.path
        assert self.start == entry.start
        assert self.end == entry.end
        self.feats.update(entry.feats)
        return

    @classmethod
    def load(klass, line):
        if not line.startswith('@'): raise ValueError(line)
        (_,_,line) = line.partition(' ')
        (path,_,line) = line.partition(' ')
        (start,_,line) = line.partition(' ')
        (end,_,line) = line.partition(' ')
        feats = {}
        for x in line.split(' '):
            (k,_,v) = x.partition('=')
            feats[k] = v
        return klass(path, int(start), int(end), feats)

def main(argv):
    import fileinput
    args = argv[1:]
    for line in fileinput.input(args):
        if line.startswith('@'):
            try:
                entry = CommentEntry.load(line.strip())
                print (entry)
            except ValueError:
                print (line)
                raise

    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
