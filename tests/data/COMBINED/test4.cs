public class Simple {
static void Main(string[] args)
{
  DemoClass myObj = new DemoClass();
  myObj.myMethod();
 DemoClass2 myObj = new DemoClass2();
  myObj.myOtherMethod();
   DemoClass m2 = new DemoClass(myObj);
   myObj.othermethod();
   Console.WriteLine(myObj.a);
   Console.WriteLine(myObj.b);
}
}