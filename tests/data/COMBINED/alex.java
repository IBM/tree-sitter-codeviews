class RandomClass {

    public void method1() {
      System.out.println("");
    }
  
    public void method2() {
      System.out.println("");
    }
  
    public void method3() {
      System.out.println("");
    }
  
    public void method4() {
      System.out.println("");
    }
  
    public void method5() {
      System.out.println("");
    }
  
    public void method6() {
      System.out.println("");
    }
  }
  
  class Dog {
  
    public void method1() {
      System.out.println("");
    }
  
    public void method2() {
      System.out.println("");
    }
  
    public void method3() {
      System.out.println("");
    }
  
    public void method4() {
      System.out.println("");
    }
  
    public void method5() {
      System.out.println("");
    }
  
    public void method6() {
      System.out.println("");
    }
  }
  
  public class Alex {
  
    static int static_variable = 4;
  
    public void function(RandomClass temp, Dog jude) {
      temp.method1();
      if (static_variable == 4) {
        temp.method2();
        return;
      } else {
        jude.method3();
        Dog joe = jude;
        joe.method4();
        jude.method5();
      }
      joe.method5(); // error
    }
  
    public static void main(String[] args) {
      RandomClass a = new RandomClass();
      Dog b = new Dog();
      function(a, b); // Assumes this is a static method of the containing class
      b.method6();
      a.whateva();
    }
  }