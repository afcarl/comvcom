//  CommentEntry.java
//
package net.tabesugi.comvcom;
import java.util.*;

public class CommentEntry {

    public String path;
    public int start;
    public int end;
    public FeatureSet feats;

    public CommentEntry(String path, int start, int end, FeatureSet feats) {
	this.path = path;
	this.start = start;
	this.end = end;
	this.feats = feats;
    }

    public CommentEntry(String s) {
	if (!s.startsWith("@")) throw new IllegalArgumentException(s);

	int i0 = s.indexOf(" ")+1; // "@"
	if (i0 == 0) throw new IllegalArgumentException(s);
	int i1 = s.indexOf(" ", i0);	// path
	if (i1 < 0) throw new IllegalArgumentException(s);
	this.path = s.substring(i0, i1);
	i0 = i1+1;
	i1 = s.indexOf(" ", i0); // start
	if (i1 < 0) throw new IllegalArgumentException(s);
	this.start = Integer.parseInt(s.substring(i0, i1));
	i0 = i1+1;
	i1 = s.indexOf(" ", i0); // end
	if (i1 < 0) throw new IllegalArgumentException(s);
	this.end = Integer.parseInt(s.substring(i0, i1));
	i0 = i1+1;
	this.feats = new FeatureSet(s.substring(i0));
    }

    public String toString() {
	return ("@ "+this.path+" "+
		this.start+" "+this.end+" "+this.feats);
    }
}
