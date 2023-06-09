public class RandomClass {
    public void method1() {
        Console.WriteLine("RandomClass.method1");
    }
    public void method19() {
        Console.WriteLine("RandomClass.method19");
    }
    public void method28() {
        Console.WriteLine("RandomClass.method28");
    }
}
public class Dog {
    public void method1() {
        Console.WriteLine("Dog.method1");
    }
    public void method19() {
        Console.WriteLine("Dog.method19");
    }
    public void method28() {
        Console.WriteLine("Dog.method28");
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
    public static void Main () {
        RandomClass a = new RandomClass();
        Dog b = new Dog();
        function(a,b);
        a.method1();
    }
}