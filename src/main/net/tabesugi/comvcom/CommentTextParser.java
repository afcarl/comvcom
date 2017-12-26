//  CommentTextParser.java
//
package net.tabesugi.comvcom;
import java.io.*;
import java.util.*;

import edu.stanford.nlp.io.*;
import edu.stanford.nlp.ling.*;
import edu.stanford.nlp.pipeline.*;
import edu.stanford.nlp.trees.*;
import edu.stanford.nlp.util.*;

public class CommentTextParser {

    StanfordCoreNLP _pipeline;

    public CommentTextParser() {
	Properties props = new Properties();
	props.setProperty("annotators", "tokenize, ssplit, pos, parse");
	_pipeline = new StanfordCoreNLP(props);
    }

    public Tree[] parse(String text) {
	Annotation annotation = new Annotation(text);
	_pipeline.annotate(annotation);
	//_pipeline.prettyPrint(annotation, out);
	//_pipeline.xmlPrint(annotation, System.out);
	List<CoreMap> sentences = annotation.get(CoreAnnotations.SentencesAnnotation.class);
	Tree[] trees = new Tree[sentences.size()];
	for (int i = 0; i < sentences.size(); i++) {
	    CoreMap sentence = sentences.get(i);
	    trees[i] = sentence.get(TreeCoreAnnotations.TreeAnnotation.class);
	}
	return trees;
    }

    public static String flatten(Tree tree) {
	assert !tree.isLeaf();
	Label label = tree.label();
	assert label != null;
	String value = label.value();
	assert value != null;
	String s = "("+value;
	for (Tree child : tree.children()) {
	    if (!child.isLeaf()) {
		s += flatten(child);
	    }
	}
	return s+")";
    }

    public static void main(String[] args)
	throws IOException {

	CommentTextParser parser = new CommentTextParser();
	for (int i = 0; i < args.length; i++) {
	    String path = args[i];
	    BufferedReader reader = new BufferedReader(new FileReader(path));
	    CommentEntry entry = null;
	    while (true) {
		String line = reader.readLine();
		if (line == null) break;
		if (line.startsWith("@")) {
		    if (entry != null) {
			System.out.println(entry);
			System.out.println();
		    }
		    entry = new CommentEntry(line);
		} else if (line.startsWith("+")) {
		    if (entry != null) {
			String text = line.substring(2);
			Tree[] trees = parser.parse(text);
			for (Tree tree : trees) {
			    entry.feats.put("parseTree", flatten(tree));
			}
		    }
		}
	    }
	    if (entry != null) {
		System.out.println(entry);
		System.out.println();
	    }
	}
    }
}
