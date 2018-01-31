/*
 Test1.java
*/

// Test1
//
public class Test1 {
    /**
     * Javadoc!
     */
    public static void main(String[] args) {
	// Do this.
	String a = foo(123); // the value.
	if (a != null) {
	    // This must be
	    // non-null.
	    System.out.print(a+"!"); /* so what */
	}
	// Newline.
	System.out.println();
        /****this is javadoc too.*****/
    }

    // Make a string.
    private static String foo(int /*notused*/ x) { // yeah.
	// Thsi.
	return "ousamanomimiwa" + //
	    "robanomimi";
    }
}
