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
        return ('<%s(%r): path=%r, start=%r, end=%r, feats=%r>' %
                (self.__class__.__name__, self.key,
                 self.path, self.start, self.end, self.feats))

    def __str__(self):
        feats = ' '.join( '%s=%s' % (k,v) for (k,v) in self.feats.items() )
        return ('@ %s %d %d %s' %
                (self.path, self.start, self.end, feats))

    def __getitem__(self, k):
        return self.feats.get(k)

    def get(self, k, v=None):
        return self.feats.get(k, v)

    def merge(self, entry):
        assert self.path == entry.path
        assert self.start == entry.start
        assert self.end == entry.end
        self.feats.update(entry.feats)
        return

    @classmethod
    def fromstring(klass, line):
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

    @classmethod
    def load(klass, fp):
        for line in fp:
            if line.startswith('@'):
                try:
                    yield klass.fromstring(line.strip())
                except ValueError:
                    raise ValueError(line)
        return

def main(argv):
    import fileinput
    args = argv[1:]
    fp = fileinput.input(args)
    for entry in CommentEntry.load(fp):
        print (entry)
    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
