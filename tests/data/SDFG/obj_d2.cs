public class DFG_A2 {
    public void main(String args[]) {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in)); // {}
        int a1 = br.attribute1; // {3}
        br.attribute1.subattribute1--; // {3,5} self loop (optional)
        br.attribute1 = 4; // {}
        int a11 = br.attribute1.subattribute1; // {3,5,6}
        br.attribute2++; // {3,8} self loop optional
        double a2 = br.attribute2; // {3,8}
        double a21 = br.attribute2.subattribute1; // {3,8}
        int sum = 2 + br.attribute1; // {3,5,6}
        int sum2 = 2 + br.attribute2; // {3,8}
        int sum3 = 2 + br.attribute1.subattribute1; // {3,5,6}
        int sum4 = 2 + br.attribute2.subattribute1; // {3,8}
    }
}

/*
 * No edges between
 * 1. br.attribute2 and br.attribute1.subattribute1.  (uncle)
 * 2. br.attribute1.subattribute1 and br.attribute2.subattribute2 (cousin)
 * 3. br.attribute1 and br.attribute2 (sibling)
 */