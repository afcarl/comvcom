//  SourceDB.java
//
package net.tabesugi.comvcom;
import java.io.*;
import java.util.*;

public class SourceDB {

    public File basedir;
    private Map<String, String> _files;

    public SourceDB(String basepath) {
	this.basedir = new File(basepath);
        _files = new HashMap<String, String>();
    }

    public String getText(String name, List<Span> spans) {
        String s = "";
        for (Span span : spans) {
            s += getText(name, span);
        }
        return s;
    }

    public String getText(String name, Span span) {
        return getText(name, span.start, span.end);
    }

    public String getText(String name, int start, int end) {
	try {
	    File file = new File(basedir, name);
            String path = file.getPath();
            String text = _files.get(path);
            if (text == null) {
                text = Utils.readFile(path);
                _files.put(path, text);
            }
	    return text.substring(start, end);
	} catch (IOException e) {
	    return null;
	}
    }

}
