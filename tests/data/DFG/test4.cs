using System;

namespace MyApplication
{
  class Program
  {
    static int MyMethod(int x, int y)
    {
      return x + y;
    }

    static void Main(string[] args)
    {
      int x = 3;
      int y = 5;
      int z = x + y;
      z = MyMethod(x, y);
      Console.WriteLine(z);
    }
  }
}