//  CommentEntry.java
//
package net.tabesugi.comvcom;
import java.util.*;

public class CommentEntry {

    public String path;
    public List<Span> spans;
    public FeatureSet feats;

    public CommentEntry(String path, List<Span> spans, FeatureSet feats) {
	this.path = path;
	this.spans = spans;
	this.feats = feats;
    }

    public CommentEntry(String s) {
	if (!s.startsWith("@")) throw new IllegalArgumentException(s);

	int i0 = s.indexOf(" ")+1; // "@"
	if (i0 == 0) throw new IllegalArgumentException(s);
	int i1 = s.indexOf(" ", i0); // path
	if (i1 < 0) throw new IllegalArgumentException(s);
	this.path = s.substring(i0, i1);
	i0 = i1+1;
	i1 = s.indexOf(" ", i0); // spans
	if (i1 < 0) throw new IllegalArgumentException(s);
        this.spans = new ArrayList<Span>();
        for (String t : s.substring(i0, i1).split(",")) {
            this.spans.add(new Span(t));
        }
	i0 = i1+1;              // feats
	this.feats = new FeatureSet(s.substring(i0));
    }

    public String toString() {
	return ("@ "+this.path+" "+Utils.join(",", this.spans)+" "+this.feats);
    }
}
