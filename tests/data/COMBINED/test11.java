class HelloWorld {
    public void something(int a) {
        this.something('a', a);
        System.out.println("How did char a get through to here?");
    }
    public void something(char a) {
        System.out.println("Always. Always. Always.");
        for(int i = 0; i<3; i++);
    }
    public void something(char a, int b) {
        System.out.println("Hit a non-static function with a different function signature");
    }
    public static void something() {
        System.out.println("Called a static function in another class");
    }
}

class Test {
    public static void something() {
        System.out.println("Hello, World!");
    }
    public static void something(int a) {
        System.out.println("Static function with 1 parameter");
    }
    public void something(int a, int b) {
        System.out.println("Non static function with 2 parameters");
    }
    public static void main(String[] args) {
        HelloWorld.something();
        new HelloWorld().something('a');
        something();
        something(0);
        Test object = new Test();
        object.something(0,1);

    }
}