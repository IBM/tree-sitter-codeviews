class Lamp {
  static boolean passedElement;
  boolean ele2;
  Lamp babylamp;
  Lamp() {
    wierdFn(passedElement);
  }
  void wierdFn(boolean somethingStatic){
    somethingStatic = true;
    newfunc(this);
  }
  void newfunc(Lamp r) {
      this.ele2 = true;
  }
}

class Main {
  static boolean fn(Lamp dog, Lamp cat) {
    cat.ele2 = true;
    dog.ele2 = false;
    cat.wierdFn(dog.babylamp.ele2);
    if (dog.ele2 != true){
        dog.ele2 = true;
    }
    return dog.ele2;
  }
  public static void main(String[] args) {
    Lamp in = new Lamp();
    Lamp out = new Lamp();
    boolean z = fn(in, out);
    System.out.println(in.ele2);
  }
}