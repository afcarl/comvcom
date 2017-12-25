//  CommentExtractor.java
//  Feature extractor for comments.
//
package net.tabesugi.comvcom;
import java.io.*;
import java.util.*;

import org.eclipse.jdt.core.*;
import org.eclipse.jdt.core.dom.*;

public class CommentExtractor extends ASTVisitor {

    static class SourceCode {

	private String _text;
	private List<Integer> _linepos = new ArrayList<Integer>();

	public SourceCode(String text) {
	    _text = text;
	    int pos = 0;
	    while (true) {
		_linepos.add(pos);
		pos = text.indexOf('\n', pos)+1;
		if (pos <= 0) break;
	    }
	}

	public String getText(int start, int end) {
	    return _text.substring(start, end);
	}

	public int getLineStart(int i) {
	    return _linepos.get(i);
	}

	public int getLineNum(int pos) {
	    int i0 = 0;
	    int i1 = _linepos.size();
	    while (i0 < i1) {
		int i = (i0+i1)/2;
		// assert i < i1;
		if (pos < _linepos.get(i)) {
		    i1 = i;
		} else {
		    i0 = i+1;
		}
	    }
	    return i0-1;
	}

	public int getCols(int pos, int tab) {
	    int start = _linepos.get(getLineNum(pos));
	    assert start <= pos;
	    int col = 0;
	    for (char c : _text.substring(start, pos).toCharArray()) {
		if (c == '\t') {
		    col = ((col/tab)+1) * tab;
		} else {
		    col++;
		}
	    }
	    return col;
	}
    }

    private SortedMap<Integer, List<ASTNode> > _start =
	new TreeMap<Integer, List<ASTNode> >();
    private SortedMap<Integer, List<ASTNode> > _end =
	new TreeMap<Integer, List<ASTNode> >();

    private Stack<ASTNode> _stack = new Stack<ASTNode>();
    private Map<ASTNode, ASTNode> _parent =
	new HashMap<ASTNode, ASTNode>();

    public void preVisit(ASTNode node) {
	addNode(node);
	if (!_stack.empty()) {
	    ASTNode parent = _stack.peek();
	    _parent.put(node, parent);
	}
	_stack.push(node);
    }

    public void postVisit(ASTNode node) {
	_stack.pop();
    }

    public void addNode(ASTNode node) {
	int start = node.getStartPosition();
	int end = node.getStartPosition() + node.getLength();
	List<ASTNode> nodes = _start.get(start);
	if (nodes == null) {
	    nodes = new ArrayList<ASTNode>();
	    _start.put(start, nodes);
	}
	nodes.add(node);
	nodes = _end.get(end);
	if (nodes == null) {
	    nodes = new ArrayList<ASTNode>();
	    _end.put(end, nodes);
	}
	nodes.add(node);
    }

    public List<ASTNode> getParentNodes(ASTNode node) {
	ArrayList<ASTNode> parents = new ArrayList<ASTNode>();
	while (node != null) {
	    parents.add(node);
	    node = _parent.get(node);
	}
	return parents;
    }

    public List<ASTNode> getNodesEndBefore(int i) {
	SortedMap<Integer, List<ASTNode> > before = _end.headMap(i+1);
	if (before.isEmpty()) return null;
	i = before.lastKey();
	return before.get(i);
    }

    public List<ASTNode> getNodesStartAfter(int i) {
	SortedMap<Integer, List<ASTNode> > after = _start.tailMap(i);
	if (after.isEmpty()) return null;
	i = after.firstKey();
	return after.get(i);
    }

    public Set<ASTNode> getNodesOutside(int start, int end) {
	Set<ASTNode> nodes0 = new HashSet<ASTNode>();
	for (List<ASTNode> nodes : _start.headMap(start+1).values()) {
	    nodes0.addAll(nodes);
	}
	Set<ASTNode> nodes1 = new HashSet<ASTNode>();
	for (List<ASTNode> nodes : _end.tailMap(end).values()) {
	    nodes1.addAll(nodes);
	}
	nodes0.retainAll(nodes1);
	return nodes0;
    }

    public FeatureSet getFeatures(SourceCode src, Comment node) {
	int start = node.getStartPosition();
	int end = start + node.getLength();
	int line = src.getLineNum(start);
	FeatureSet fset = new FeatureSet();
	fset.put("type", getType(node));
	fset.put("line", line);

	List<ASTNode> before = getNodesEndBefore(start);
	if (before != null) {
	    ASTNode n = before.get(0);
	    int line1 = src.getLineNum(n.getStartPosition()+n.getLength());
	    fset.put("leftTypes", toKeySorted(before));
	    fset.put("leftLine", line1);
	}

	List<ASTNode> after = getNodesStartAfter(end);
	if (after != null) {
	    ASTNode n = after.get(0);
	    int line1 = src.getLineNum(n.getStartPosition());
	    fset.put("rightTypes", toKeySorted(after));
	    fset.put("rightLine", line1);
	}

	Collection<ASTNode> outside = getNodesOutside(start, end);
	ASTNode parent = null;
	for (ASTNode n : outside) {
	    if (n == node) continue;
	    if (parent == null || n.getLength() < parent.getLength()) {
		parent = n;
	    }
	}
	assert parent != null;
	List<ASTNode> parents = getParentNodes(parent);
	fset.put("parentTypes", toKey(parents));
	int pstart = parent.getStartPosition();
	int pend = pstart + parent.getLength();
	fset.put("parentStart", (pstart == start));
	fset.put("parentEnd", (pend == end));

	return fset;
    }

    private static String getType(ASTNode node) {
	int type = node.getNodeType();
	return Utils.getASTNodeTypeName(type);
    }

    private static String toKey(List<ASTNode> nodes) {
	String[] names = new String[nodes.size()];
	for (int i = 0; i < nodes.size(); i++) {
	    names[i] = getType(nodes.get(i));
	}
	return Utils.join(",", names);
    }

    private static String toKeySorted(Collection<ASTNode> nodes) {
	ASTNode[] sorted = new ASTNode[nodes.size()];
	nodes.toArray(sorted);
	Arrays.sort(sorted, (a, b) -> (a.getLength() - b.getLength()));
	String[] names = new String[sorted.length];
	for (int i = 0; i < sorted.length; i++) {
	    names[i] = getType(sorted[i]);
	}
	return Utils.join(",", names);
    }

    @SuppressWarnings("unchecked")
    public static void main(String[] args)
	throws IOException {

	int tab = 8;
	List<String> files = new ArrayList<String>();
	PrintStream out = System.out;
	for (int i = 0; i < args.length; i++) {
	    String arg = args[i];
	    if (arg.equals("--")) {
		for (; i < args.length; i++) {
		    files.add(args[i]);
		}
	    } else if (arg.equals("-o")) {
		out = new PrintStream(new FileOutputStream(args[i+1]));
		i++;
	    } else if (arg.equals("-t")) {
		tab = Integer.parseInt(args[i]);
		i++;
	    } else if (arg.startsWith("-")) {
	    } else {
		files.add(arg);
	    }
	}

	String[] srcpath = { "." };
	for (String path : files) {
	    Utils.logit("Parsing: "+path);
	    String srctext = Utils.readFile(path);

	    Map<String, String> options = JavaCore.getOptions();
	    JavaCore.setComplianceOptions(JavaCore.VERSION_1_7, options);
	    ASTParser parser = ASTParser.newParser(AST.JLS8);
	    parser.setUnitName(path);
	    parser.setSource(srctext.toCharArray());
	    parser.setKind(ASTParser.K_COMPILATION_UNIT);
	    parser.setResolveBindings(false);
	    parser.setEnvironment(null, srcpath, null, true);
	    parser.setCompilerOptions(options);
	    CompilationUnit cu = (CompilationUnit)parser.createAST(null);

	    SourceCode src = new SourceCode(srctext);
	    CommentExtractor visitor = new CommentExtractor();
	    cu.accept(visitor);

            for (Comment node : (List<Comment>) cu.getCommentList()) {
		visitor.addNode(node);
	    }

	    Comment node0 = null;
            for (Comment node1 : (List<Comment>) cu.getCommentList()) {
		int start1 = node1.getStartPosition();
		int end1 = start1 + node1.getLength();
		if (node1 instanceof Javadoc) {
		    start1 += 3;
		    end1 -= 2;
		} else if (node1 instanceof BlockComment) {
		    start1 += 2;
		    end1 -= 2;
		} else {
		    start1 += 2;
		}
		FeatureSet feats1 = visitor.getFeatures(src, node1);
		feats1.put("cols", src.getCols(node1.getStartPosition(), tab));
		if (node0 != null) {
		    int start0 = node0.getStartPosition();
		    int end0 = start0 + node0.getLength();
		    int line0 = src.getLineNum(end0);
		    int cols0 = src.getCols(start0, tab);
		    feats1.put("prevLine", line0);
		    feats1.put("prevCols", cols0);
		}
		CommentEntry comm = new CommentEntry(path, start1, end1, feats1);
		out.println(comm);
		String s = src.getText(start1, end1);
		out.println("+ "+s.replace("\n", " "));
		out.println();
		node0 = node1;
	    }
	}

	out.close();
    }
}
