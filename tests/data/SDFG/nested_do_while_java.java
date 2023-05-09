public class Max {
    public static void main (String[] args) {
        int i = 0;

        do
        {
            System.out.println("Value of i: {0}", i);
            int j = i;

            i++;

            do
            {
                System.out.println("Value of j: {0}", j);
                j++;
            } while (j == 2);

        } while (i < 2);
    }
}