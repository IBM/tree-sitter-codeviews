public class DFG_A2 {
    public void main(string[] args) {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in)); // {}
        String str = br.attribute1; // {3}
        str = br.attribute2.method1(); // {3}
        br.attribute1 = br.attribute2; // {3,5}
        br.method2(br.attribute1, br.attribute2); // {3,5,6}
        BufferedReader br2 = br; // {5,6,7}
        br.method3(); // {5,6,7}
        int j = br2.attribute1.method2(3,4); // {8}
    }
}

//str = br.attribute2.method1(); // {3}
//// assume method only affects br.attribute2 (Current Impl)
//// but can also affect br (Option 2)
//br.attribute2 = a;
//br.attribute2.a = b;
//// keep both whenever br.attribute2 is used
//int hello = br.attribute2.a.b // {}
//br.attribute1 = br.attribute2; // {3,5}
//attribute1 = br.attribute2; // {5}