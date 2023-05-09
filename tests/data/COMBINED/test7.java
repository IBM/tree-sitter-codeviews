class A{
    boolean isOn;
    static int j;
    A(){
        isOn = false;
    }
    static String z(){
        System.out.println(j);
        return "z";
    }
}

class Main {
  public static void main(String[] args) {
    A.z();
  }
}