#!/usr/bin/env python
import sys

class CommentEntry:

    def __init__(self, path, spans, feats, key=None):
        self.path = path
        self.spans = spans
        self.feats = feats
        self.key = key
        return

    def __repr__(self):
        return ('<%s(%r): path=%r, start=%r, end=%r, feats=%r>' %
                (self.__class__.__name__, self.key,
                 self.path, self.start, self.end, self.feats))

    def __str__(self):
        spans = ','.join( '%d:%d' % (s,e) for (s,e) in self.spans )
        feats = ' '.join( '%s=%s' % (k,v) for (k,v) in self.feats.items() )
        return ('@ %s %s %s' % (self.path, spans, feats))

    def __getitem__(self, k):
        return self.feats.get(k)

    def __setitem__(self, k, v):
        self.feats[k] = v
        return

    def __contains__(self, k):
        return k in self.feats

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
        (ss,_,line) = line.partition(' ')
        spans = []
        for x in ss.split(','):
            (s,_,e) = x.partition(':')
            spans.append((int(s), int(e)))
        feats = {}
        for x in line.split(' '):
            (k,_,v) = x.partition('=')
            feats[k] = v
        return klass(path, spans, feats)

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
