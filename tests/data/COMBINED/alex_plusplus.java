class RandomClass {
    public void method1() {
        System.out.println("RandomClass.method1");
    }
    public void method19() {
        System.out.println("RandomClass.method19");
    }
    public void method28() {
        System.out.println("RandomClass.method28");
    }
}
class Dog {
    public void method1() {
        System.out.println("Dog.method1");
    }
    public void method19() {
        System.out.println("Dog.method19");
    }
    public void method28() {
        System.out.println("Dog.method28");
    }
}
public class Alex {
    // public static void function(RandomClass temp, Dog jude) {
    public void function(RandomClass temp, Dog jude) {
        temp.method1();
        if (static_variable == 4) {
            temp.method1();
            return;
        }
        else {
            jude.method1();
            Dog joe = jude;
            joe.method1();
            jude.method1();
        }
        test(temp,jude);
        temp.method19();
    }
    public static void test(RandomClass delhi, Dog bangalore) {
        delhi.method1();
        RandomClass mumbai = delhi;
        mumbai.method1();
        if (another_static_variable) {
            mumbai.method28();
        }
        else{
            bangalore.method1();
        }
    }
    public static void main (String[] args) {
        RandomClass a = new RandomClass();
        Dog b = new Dog();
        function(a,b);
        a.method1();
    }
}