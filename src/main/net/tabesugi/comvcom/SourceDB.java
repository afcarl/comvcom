//  SourceDB.java
//
package net.tabesugi.comvcom;
import java.io.*;

public class SourceDB {

    public File basedir;

    public SourceDB(String basepath) {
	this.basedir = new File(basepath);
    }

    public String getText(String name, int begin, int end) {
	try {
	    File file = new File(basedir, name);
	    String text = Utils.readFile(file);
	    return text.substring(begin, end);
	} catch (IOException e) {
	    return null;
	}
    }

}
