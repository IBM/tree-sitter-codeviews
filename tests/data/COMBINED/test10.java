public class Student
{

public String name;

public Student (String stuName) {
name = stuName;
}

private int marks;

public void setMarks(int stuMar) {
marks = stuMar;
}

// This method prints the student details.
public void printStu() {
System.out.println("Name: " + name );
System.out.println("Marks:" + marks);
}

public static void main(String args[]) {
Student StuOne = new Student("Ross");
Student StuTwo = new Student("Rachel");
Student StuThree = new Student("Phoebe");

StuOne.setMarks(98);
StuTwo.setMarks(89);
StuThree.setMarks(90);

StuOne.printStu();
StuTwo.printStu();
StuThree.printStu();

}
}