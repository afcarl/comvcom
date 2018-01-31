#!/usr/bin/env python
import sys
import os.path
from comment import CommentEntry
from srcdb import SourceDB, SourceMap

BASEDIR = os.path.dirname(__file__)

def q(s):
    return s.replace('&','&amp;').replace('>','&gt;').replace('<','&lt;').replace('"','&quot;')

def show_html_headers():
    print('''<!DOCTYPE html>
<html>
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
    print('''
<body onload="run('a')">
<h1>Comment Tagging Experiment</h1>

<h2>Your Mission</h2>
<ul>
<li> Classify 100 comments in the following code snippets.
<li> For each comment (marked <mark>like this</mark>), choose its type from the menu.<br>
  A comment type is defined by the following eleven <strong>Categories</strong>.<br>
  When multiple categories apply, choose the most dominant category.<br>
<li> Check the grammar of each comment.  When a comment is written in English,<br>
  and its type is not "Comment Out", "Visual Cue", "Directive" or "Uncategorized",<br>
  check the <label class=head><input type=checkbox> Ung?</label> checkbox
  if it is ungrammatical or has a large omission.
<li> When a comment is written in non-English, use a translator <br>
  to get the proper meaning.
  (e.g. <a target="translator" href="https://translate.google.com/">translate.google.com</a>)
<li> When a marked line is a part of a larger comment, <br>
  consider the category of the entire comment.<br>
  Otherwise, ignore unmarked comments in the snippets.
<li> For getting a wider context, click the link in each snippet.<br>
  It opens the original source code.
<li> Your choices are saved in the follwoing textbox:<br>
  <textarea id="a" cols="80" rows="4" spellcheck="false" autocomplete="off"></textarea><br>
  When finished, send the above content (from <code>#START</code> to <code>#END</code>) to
  the experiment organizer.<br>
<li> <u class=caution><strong>Caution:</strong>
  Do not consult others about the code comments during this experiment.</u>
</ul>

<h2>Categories</h2>
<table border>
<tr><th>Label</th><th>Description</th><tr>
<tr><td>m: Meta Info.</td>
<td>Meta information such as author, date, or copyright info.
<pre>
<mark>// from org.apache.curator.framework.CuratorFrameworkFactory</mark>
this.maxCloseWait = 1000;
</pre>
</td></tr>
<tr><td>o: Value Desc.</td>
<td>Noun phrase that describes a variable, constant or condition.
<pre>
addSourceFolders(
    SourceFolder.FACTORY,
    getSourceFoldersToInputsIndex(target.getInputs()),
    false <mark>/* wantsPackagePrefix */</mark>,
    context);
</pre>
</td></tr>
<tr><td>a: Precondition</td>
<td>Conditions that hold <u>before</u> the code is executed.<br>
Typically used for explaining "why" this code is needed.
<pre>
<mark>// Unable to find the specidifed document.</mark>
return Status.ERROR;
</pre>
<pre>
if (myStatusBar != null) { <mark>//not welcome screen</mark>
  myStatusBar.addProgress(this, myInfo);
}
</pre>
</td></tr>
<tr><td>p: Postcondition</td>
<td>What is achieved <u>after</u> the code is executed.<br>
Typically used for explaining "what" this code does.
<pre>
<mark>// create some test data</mark>
Map&lt;String, String&gt; data = createTestData(testSize);
</pre>
<pre>
<mark>// if we had a prior association, restore and throw an exception</mark>
if (previous != null) {
        taskVertices.put(id, previous);
</pre>
</td></tr>
<tr><td>t: Type/Enum/Iface</td>
<td>Description of a type, class, enumeration, or interface.
<pre>
<mark>// Comparison function</mark>
class MyComparator implements Comparator {
    public int compare(Object o1, Object o2) {
</pre>
</td></tr>
<tr><td>i: Instruction</td>
<td>Instruction for <u>code maintainers</u>. So-called "task comments".
<pre>
<mark>// TODO Auto-generated catch block</mark>
e.printStackTrace();
Assert.fail("Failed");
</pre>
</td></tr>
<tr><td>g: Guide</td>
<td>Instruction for <u>code users</u>. Not to be confused with Instructions.
<pre>
<mark>// Example: a = doit();</mark>
</pre>
</td></tr>
<tr><td>c: Comment Out</td>
<td>Commented out code.
<pre>
while ((m = ch.receive()) != null) {
    <mark>//System.out.println(Strand.currentStrand() + ": " + m);</mark>
    long index = ((TickerChannelConsumer)ch).getLastIndexRead();
</pre>
</td></tr>
<tr><td>v: Visual Cue</td>
<td>Text inserted just for the ease of reading.
<pre>
<mark>//
// Initialization key storage
//</mark>
</pre>
</td></tr>
<tr><td>d: Directive</td>
<td>Compiler directive that isn't directed to human readers.
<pre>
<mark>//CHECKSTYLE:OFF</mark>
} catch (final Exception ex) {
<mark>//CHECKSTYLE:ON</mark>
</pre>
</td></tr>
<tr><td>u: Uncategorized</td>
<td>All other comments that cannot be categorized.
</td></tr>
</table>
''')
    return

def show(cid, src, spans, key, url, ncontext=4):
    ranges = [(s,e,True) for (s,e) in spans]
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
        print('usage: %s [-B basedir] [-M srcmap.db] '
              '[-c context] out.comm' %
              argv[0])
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'B:M:c:')
    except getopt.GetoptError:
        return usage()
    srcdb = None
    srcmap = None
    ncontext = 4
    for (k, v) in opts:
        if k == '-B': srcdb = SourceDB(v)
        elif k == '-M': srcmap = SourceMap(v)
        elif k == '-c': ncontext = int(v)
    if not args: return usage()

    show_html_headers()

    fp = fileinput.input(args)
    index = 0
    for e in CommentEntry.load(fp):
        src = srcdb.get(e.path)
        url = srcmap.geturl(e.path)
        cid = 'c%03d' % index
        show(cid, src, e.spans, e.key, url, ncontext=ncontext)
        index += 1

    return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
