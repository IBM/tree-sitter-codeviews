public class Max {
    public static void Main (String[] args) {
        int i = 0;

do
{
    Console.WriteLine("Value of i: {0}", i);
    int j = i;

    i++;

    do
    {
        Console.WriteLine("Value of j: {0}", j);
        j++;
    } while (j < 2);

} while (i < 2);
    }
}