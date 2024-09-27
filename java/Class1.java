public class Class1 {
    private String privateVar;

    public Class1() {
        this.privateVar = "I'm private";
    }

    public void method1() {
        System.out.println("This is method1 from Class1");
        privateMethod();
    }

    private void privateMethod() {
        System.out.println("This is a private method in Class1");
        System.out.println("Private var: " + privateVar);
    }
}