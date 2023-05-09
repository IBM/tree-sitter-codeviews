public class Simple {
  public static void main(String[] args) {
    int j = 0;
    for (int i = 0; i < 10; i++) {
      System.out.println(j);
      for (j = 0; j < 10; j++) {
        System.out.println(j);
        System.out.println(i);
        j += 1;
        if (j == 9)
          i = 999;
      }
      if (i == 999) {
        System.out.println(i);
        System.out.println("o.O");
      }
      j += 1;
    }
    for (int i = 0; i < 10; i++) {
      System.out.println(j);
      for (j = 0; j < 10; j++) {
        System.out.println(j);
        System.out.println(i);
        j += 1;
      }
      j += 1;
    }
  }
}