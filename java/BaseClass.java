public class BaseClass {
    protected String baseVar;

    public BaseClass() {
        this.baseVar = "I'm a base class variable";
    }

    public void baseMethod() {
        System.out.println("This is a method from BaseClass");
        System.out.println("Base var: " + baseVar);
    }

    // Demonstrate generic method
    public <T> void printArray(T[] array) {
        for (T element : array) {
            System.out.print(element + " ");
        }
        System.out.println();
    }
}