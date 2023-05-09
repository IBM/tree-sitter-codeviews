class Student {

  int rollno = 1;
  String name;
  static String college = "KV INS Hamla"; //static variable
  float fee;

  Student(int rollno, String name, float f) {
    this.name = name;
    this.rollno += this.rollno;
    this.rollno = rollno;
    fee = f;
  }

  void display() {
    String college = college + "a";
    System.out.println(college + " " + rollno + " " + name + " " + this.fee);
    System.out.println(
      Student.college + " " + rollno + " " + name + " " + this.fee
    );
    System.out.println(
      this.college + " " + rollno + " " + name + " " + this.fee
    );
    System.out.println(
      TestThis2.college + " " + rollno + " " + name + " " + this.fee
    );
  }
}

class TestThis2 {

  static String college = "KV IIT Powai";

  public static void main(String args[]) {
    Student s1 = new Student(111, "ankit", 5000f);
    // Student s2 = new Student(112, "sumit", 6000f);
    // s1.display();
    // s2.display();
  }
}
