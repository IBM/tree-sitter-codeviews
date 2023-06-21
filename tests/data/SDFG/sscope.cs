public class Max{
    static int max (int a, int b)  {
        int max = 0;
        if (a < b) {
             max = b;
         } else {
           max = a;
        }
        int cheetah = 0;
        do
        {
            Console.WriteLine(cheetah);
            cheetah = cheetah + 1;
        } while(cheetah < 5);
         return max;
     }
}