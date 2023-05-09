public class Simple {
static void Main(string[] args){
  int j = 0;
  for (int i=0; i<10; i++){
    Console.WriteLine(j);
    for (j=0; j<10; j++){
        Console.WriteLine(j);
        Console.WriteLine(i);
        j+=1;
        if (j == 9)
        i = 999;
      }
    if (i==999)
    {
    Console.WriteLine(i);
    Console.WriteLine("o.O");
    }
    j+=1;
  }
  for (int i=0; i<10; i++){
    Console.WriteLine(j);
    for (j=0; j<10; j++){
        Console.WriteLine(j);
        Console.WriteLine(i);
        j+=1;
      }
    j+=1;
  }
//  THE FOLLOWING FAIL?
//  for (dynamic x = 0, y = new MyClass { a = 20, b = 30 }; x < 100; x++, y.a++, y.b--) {
//        Console.Write("X=" + x + " (" + x.GetType() + "\n" +
//                      "Y.a=" + y.a + ",Y.b=" + y.b + " (" + y.GetType() + "\n");

//for (int i = 0, k = 1; k < 3; k++, i++){
//        Console.WriteLine(i);
//}

//  for (var (i, j) = (0, (MyClass) 1); j < 3; i++, j++)
//    {
//        Console.WriteLine(i);
//    }
}
}