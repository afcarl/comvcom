//  FeatureSet.java
//
package net.tabesugi.comvcom;
import java.util.*;

public class FeatureSet {

    private Map<String, String> _feats =
	new HashMap<String, String>();

    public FeatureSet() {
    }

    public FeatureSet(String s) {
	for (String entry : s.split(" ")) {
	    int i = entry.indexOf("=");
	    if (i < 0) throw new IllegalArgumentException(s);
	    String key = entry.substring(0, i);
	    String value = entry.substring(i+1);
	    _feats.put(key, value);
	}
    }

    public void put(String key, int value) {
	_feats.put(key, Integer.toString(value));
    }
    public void put(String key, boolean value) {
	_feats.put(key, Boolean.toString(value));
    }
    public void put(String key, String value) {
	_feats.put(key, value);
    }

    public String get(String key) {
	return _feats.get(key);
    }

    public String toString() {
	String s = null;
	for (Map.Entry<String, String> entry : _feats.entrySet()) {
	    if (s == null) {
		s = "";
	    } else {
		s += " ";
	    }
	    s += entry.getKey()+"="+entry.getValue();
	}
	return s;
    }

}
