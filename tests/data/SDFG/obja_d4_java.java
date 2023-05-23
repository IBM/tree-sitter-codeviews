public class DFG_A2 {
    public void main(string[] args) {
        int arr[4] = {1,2,3,4}; //{}
        Object obj = new Object(); // {}
        obj.sum = obj.a; // {4}
        for(int i = 0; i<4; i++) { // {6} optional self loop
            obj.sum+=arr[i]; // {3,4,5,6}
            int unused = 0;
            unused = unused / obj.sum;
        }
    }
}