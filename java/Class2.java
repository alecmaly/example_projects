public class Class2 {
    public static void function1() {
        System.out.println("This is function1 from Class2");
        internalFunction();
    }

    private static void internalFunction() {
        System.out.println("This is an internal function in Class2");
    }
}