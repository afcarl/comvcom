// $ javac -cp stanford-corenlp-3.8.0.jar TestCoreNLP.java
// $ java -cp .:stanford-corenlp-3.8.0.jar:stanford-corenlp-3.8.0-models.jar:ejml-0.23.jar TestCoreNLP

import java.io.*;
import java.util.*;

import edu.stanford.nlp.io.*;
import edu.stanford.nlp.ling.*;
import edu.stanford.nlp.pipeline.*;
import edu.stanford.nlp.trees.*;
import edu.stanford.nlp.util.*;

public class TestCoreNLP {

    public static void main(String[] args) throws IOException {

	Properties props = new Properties();
	props.setProperty("annotators", "tokenize, ssplit, pos, parse");

	StanfordCoreNLP pipeline = new StanfordCoreNLP(props);

	Annotation annotation;
	if (args.length > 0) {
	    annotation = new Annotation(args[0]);
	} else {
	    annotation = new Annotation("Don't do this dude.");
	}
	pipeline.annotate(annotation);

	//pipeline.prettyPrint(annotation, System.out);
	//pipeline.xmlPrint(annotation, System.out);

	List<CoreMap> sentences = annotation.get(CoreAnnotations.SentencesAnnotation.class);
	for (CoreMap sentence : sentences) {
	    List<CoreLabel> tokens = sentence.get(CoreAnnotations.TokensAnnotation.class);
	    if (tokens != null) {
		for (CoreLabel token : tokens) {
		    String pos = token.getString(CoreAnnotations.PartOfSpeechAnnotation.class);
		    System.out.println(pos);
		}
	    }
	    Tree tree = sentence.get(TreeCoreAnnotations.TreeAnnotation.class);
	    if (tree != null) {
		System.out.println("parse:");
		tree.pennPrint(System.out);
		doit(tree, 0);
		System.out.println();
	    }
	}

    }

    private static void doit(Tree tree, int level) {
	Label label = tree.label();
	if (label != null) {
	    System.out.println(level+": "+label.value());
	}
	for (Tree child : tree.children()) {
	    if (!child.isLeaf()) {
		doit(child, level+1);
	    }
	}
    }
}
