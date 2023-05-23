public class Max {
    public static void main (String[] args) {
        switch (day)
            {
              case 1:
                Console.WriteLine("Monday");
              case 2:
                switch (day)
                {
                  case 5:
                    Console.WriteLine("Friday");
                    break;
                  case 6:
                    Console.WriteLine("Saturday");
                    break;
                  case 7:
                    Console.WriteLine("Sunday");
                    break;
                  default:
                    Console.WriteLine("Tuesday");
                }
                Console.WriteLine("Tuesday");
                break;
              case 3:
                Console.WriteLine("Wednesday");
                break;
              case 4:
                Console.WriteLine("Thursday");
                break;
              case 5:
                Console.WriteLine("Friday");
                break;
              case 6:
                Console.WriteLine("Saturday");
                break;
              case 7:
                Console.WriteLine("Sunday");
                break;
            }
            Console.WriteLine("Sunday");
    }
}