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

    public CoreMap parse(String text) {
	Annotation annotation = new Annotation(text);
	_pipeline.annotate(annotation);
	//_pipeline.prettyPrint(annotation, System.out);
	//_pipeline.xmlPrint(annotation, System.out);
	// Only returns the first sentence.
	List<CoreMap> sentences = annotation.get(CoreAnnotations.SentencesAnnotation.class);
	if (sentences.size() == 0) return null;
	return sentences.get(0);
    }

    public static boolean isCodeLike(String text) {
        final String CODEPAT = ".*([=_{}%@]|\\w\\.\\w|\\w\\().*|.*[;:]\\s*$";
        return text.matches(CODEPAT);
    }

    public static String getWords(CoreMap sentence) {
	List<CoreLabel> tokens = sentence.get(CoreAnnotations.TokensAnnotation.class);
	List<String> syms = new ArrayList<String>();
	for (CoreLabel token : tokens) {
	    String word = token.getString(CoreAnnotations.TextAnnotation.class);
	    if (Utils.isLetter(word)) {
		syms.add(word.toLowerCase());
	    }
	}
	return Utils.join(",", syms);
    }

    public static String getPos(CoreMap sentence) {
	List<CoreLabel> tokens = sentence.get(CoreAnnotations.TokensAnnotation.class);
	List<String> syms = new ArrayList<String>();
	for (CoreLabel token : tokens) {
	    String pos = token.getString(CoreAnnotations.PartOfSpeechAnnotation.class);
	    if (Utils.isLetter(pos)) {
                syms.add(pos);
            }
	}
	return Utils.join(",", syms);
    }

    public static String flatten(CoreMap sentence, int level) {
	Tree tree = sentence.get(TreeCoreAnnotations.TreeAnnotation.class);
	List<String> syms = new ArrayList<String>();
	visit(syms, tree, level);
	return Utils.join(",", syms);
    }

    public static void visit(List<String> syms, Tree tree, int level) {
	if (!tree.isLeaf()) {
	    for (Tree child : tree.children()) {
		if (level == 0) {
		    Label label = child.label();
		    String value = label.value();
		    syms.add(value);
		} else {
		    visit(syms, child, level-1);
		}
	    }
	}
    }

    public static void main(String[] args)
	throws IOException {

	SourceDB src = new SourceDB(args[0]);
	CommentTextParser parser = new CommentTextParser();
	for (int i = 1; i < args.length; i++) {
	    String path = args[i];
	    BufferedReader reader = new BufferedReader(new FileReader(path));
	    while (true) {
		String line = reader.readLine();
		if (line == null) break;
		if (line.startsWith("@")) {
		    CommentEntry entry = new CommentEntry(line);
		    String text = src.getText(entry.path, entry.spans);
		    CoreMap sentence = parser.parse(text);
		    if (sentence != null) {
			entry.feats.put("words", getWords(sentence));
			entry.feats.put("posTags", getPos(sentence));
			entry.feats.put("parseLevel1", flatten(sentence, 0));
			entry.feats.put("parseLevel2", flatten(sentence, 1));
		    }
                    entry.feats.put("codeLike", isCodeLike(text));

		    System.out.println(entry);
		    System.out.println();
		}
	    }
	}
    }
}
