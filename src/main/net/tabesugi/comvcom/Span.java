//  Span.java
//
package net.tabesugi.comvcom;

public class Span extends Object {

    public int start;
    public int end;

    public Span(int start, int end) {
        this.start = start;
        this.end = end;
    }

    public Span(String s) {
        int i = s.indexOf(':');
        this.start = Integer.parseInt(s.substring(0, i));
        this.end = Integer.parseInt(s.substring(i+1));
    }

    public String toString() {
        return (this.start+":"+this.end);
    }

}
