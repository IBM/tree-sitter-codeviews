public class Tester {
    public static void main(String args[]) {
        int greeting = 8;
 
        int value = switch (greeting) {
            case "hi" -> {
                System.out.println("I am not just yielding!");
                yield 1;
            }
            case "hello" -> {
                System.out.println("Me too.");
                yield 2;
            }
            default -> {
                System.out.println("OK");
                yield -1;
            }
        };
        //int s = 5;
    }
 }