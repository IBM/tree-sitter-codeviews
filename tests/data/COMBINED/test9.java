class Lamp {
  static boolean passedElement;
  boolean ele2;
  Lamp() {
    wierdFn(passedElement);
  }
  void wierdFn(boolean somethingStatic){
    somethingStatic = true;
  }
}

class Main {
  static boolean fn(Lamp dog, Lamp cat) {
    cat.ele2 = true;
    Lamp temp = dog;
    temp.ele2 = false;
    return dog.ele2;
  }
  public static void main(String[] args) {
    Lamp in = new Lamp();
    Lamp out = new Lamp();
    boolean z = fn(in, out);
    System.out.println(in.ele2);
  }
}