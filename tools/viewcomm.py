#!/usr/bin/env python
import sys
import os.path
from comment import CommentEntry
from srcdb import SourceDB, SourceMap

BASEDIR = os.path.dirname(__file__)

def q(s):
    return s.replace('&','&amp;').replace('>','&gt;').replace('<','&lt;').replace('"','&quot;')

def show_html_headers():
    print('''<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style>
pre { margin: 1em; background: #eeeeee; }
.head { font-size: 75%; font-weight: bold; }
.src { margin: 8px; padding: 4px; border: 2px solid gray; }
.key { font-weight: bold; }
</style>
''')
    with open(os.path.join(BASEDIR, 'helper.js')) as fp:
        print('<script>')
        print(fp.read())
        print('</script>')
    print('<body onload="run(\'a\')">')
    print('<textarea id="a" cols="80" rows="4" spellcheck="false" autocomplete="off"></textarea>')
    return

def show(cid, src, spans, key, url=None, ncontext=4):
    ranges = [(s,e,True) for (s,e) in spans]
    if url is None:
        print('# %s:' % cid)
        print('@ %s %r key=%s' % (src.name, spans, key))
        for (_,line) in src.show(ranges, ncontext=ncontext):
            print('  '+line, end='')
        print()
    else:
        lines = []
        linenos = set()
        for (lineno,line) in src.chunk(ranges, ncontext=ncontext):
            if lineno is None:
                lines.append('       ...')
            else:
                buf = ''
                for (v, anno, s) in line:
                    if v == 0:
                        s = s.replace('\n','')
                        buf += q(s)
                        if anno:
                            linenos.add(lineno)
                    elif v < 0:
                        buf += '<mark>'
                    else:
                        buf += '</mark>'
                lines.append('%5d: %s' % (lineno+1, buf))
        assert linenos
        name = os.path.basename(src.name)
        lineno0 = min(linenos)+1
        lineno1 = max(linenos)+1
        print('<div class=src><div class=head>%s:' % (cid))
        print('<span id="%s" class=ui> </span>' % (cid))
        print('<a target="original" href="%s#L%d-L%d">%s</a></div>' %
              (q(url), lineno0, lineno1, name))
        if key is not None:
            print('<div class=key>key=%s</div>' % (q(key)))
        print('<pre>')
        for line in lines:
            print(line)
        print('</pre></div>\n')
    return

def main(argv):
    import fileinput
    import getopt
    def usage():
        print('usage: %s [-B basedir] [-M srcmap.db] [-H] '
              '[-c context] comm.out' %
              argv[0])
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'B:M:Hc:')
    except getopt.GetoptError:
        return usage()
    srcdb = None
    srcmap = None
    html = False
    ncontext = 4
    for (k, v) in opts:
        if k == '-B': srcdb = SourceDB(v)
        elif k == '-M': srcmap = SourceMap(v)
        elif k == '-H': html = True
        elif k == '-c': ncontext = int(v)
    if not args: return usage()

    if html:
        show_html_headers()

    fp = fileinput.input(args)
    index = 0
    for e in CommentEntry.load(fp):
        src = srcdb.get(e.path)
        url = None
        if html and srcmap is not None:
            url = srcmap.geturl(e.path)
        cid = 'c%03d' % index
        show(cid, src, e.spans, e.key, url=url, ncontext=ncontext)
        index += 1

    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
