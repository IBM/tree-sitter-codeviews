public class DFG_A1 {
    public void main(string[] args) {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in)); // {}
        String str = br.attribute1; // {3} Incoming information from declaration of br from line 1
        str = br.attribute2; // {3} Incoming information from declaration of br from line 1
        br.attribute1 = br.attribute2; // {3} Incoming information from declaration of br from line 1
        method_call(br.attribute1, br.attribute2); // {3,6}
        BufferedReader br2 = br; // {3,6}
    }
}

/*
 * No edges between
 * 1. br.attribute2 and br.attribute1.subattribute1.  (uncle)
 * 2. br.attribute1.subattribute1 and br.attribute2.subattribute2 (cousin)
 * 3. br.attribute1 and br.attribute2 (sibling)
 */