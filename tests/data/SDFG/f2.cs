using System;

namespace ConsoleApplication1
{
    public class Sentence
    {
        private readonly object balanceLock = new object();
        private decimal balance;
       public Sentence(string s)
       {
          Value = s;
          decimal appliedAmount = 0;
            lock (balanceLock)
            {
                if (balance >= amount)
                {
                    balance -= amount;
                    appliedAmount = amount;
                }
            }
            return appliedAmount;
       }

       public string Value { get; set; }

       public char GetFirstCharacter()
       {
          try
          {
             return Value[0];
          }
          catch (NullReferenceException e)
          {
             throw;
          }
       }
    }
    class Program
    {
    double getAverage(int[] arr, int size) {
         int i;
         double avg;
         int sum = 0;
         int val = 2;
         Debug.Assert(val != 2, " Value should not be 2.");
         for (i = 0; i < size; ++i) {
            sum += arr[i];
         }
         var s = new Sentence(null);
         Console.WriteLine($"The first character is {s.GetFirstCharacter()}");
         avg = (double)sum / size;
         return avg;
      }
    static void Main(string[] args)
    {
        Program app = new Program();
        /* an int array with 5 elements */
         int [] balance = new int[]{1000, 2, 3, 17, 50};
         double avg;

         /* pass pointer to the array as an argument */
         avg = app.getAverage(balance, 5 ) ;
        int number = 0;

        while(number < 5)
        {
        Console.WriteLine(number);
        number = number + 1;
        }

        Console.ReadLine();
        int number = 0;
        do
        {
            Console.WriteLine(number);
            number = number + 1;
        } while(number < 5);
        int number = 5;

        for(int i = 0; i < number; i++)
        Console.WriteLine(i);

        for (int outer = 0; outer < 5; outer++)
        {
            for (int inner = 0; inner < 5; inner++)
            {
                if (inner > outer)
                {
                    break;
                }

                Console.Write($"{inner} ");
            }
            Console.WriteLine();
        }
        foreach (int i in ProduceEvenNumbers(9))
        {
            Console.Write(i);
            Console.Write(" ");
        }
        // Output: 0 2 4 6 8

        IEnumerable<int> ProduceEvenNumbers(int upto)
        {
            for (int i = 0; i <= upto; i += 2)
            {
                yield return i;
            }
        }

        Console.ReadLine();
        var matrices = new Dictionary<string, int[][]>
        {
            ["A"] = new[]
            {
                new[] { 1, 2, 3, 4 },
                new[] { 4, 3, 2, 1 }
            },
            ["B"] = new[]
            {
                new[] { 5, 6, 7, 8 },
                new[] { 8, 7, 6, 5 }
            },
        };

        CheckMatrices(matrices, 4);

        void CheckMatrices(Dictionary<string, int[][]> matrixLookup, int target)
        {
            foreach (var (key, matrix) in matrixLookup)
            {
                for (int row = 0; row < matrix.Length; row++)
                {
                    for (int col = 0; col < matrix[row].Length; col++)
                    {
                        if (matrix[row][col] == target)
                        {
                            goto Found;
                        }
                    }
                }
                Console.WriteLine($"Not found {target} in matrix {key}.");
                continue;

            Found:
                Console.WriteLine($"Found {target} in matrix {key}.");
            }
        }
    }
    }
}