public class DerivedClass extends BaseClass {
    private String derivedVar;

    public DerivedClass() {
        super();
        this.derivedVar = "I'm a derived class variable";
    }

    @Override
    public void baseMethod() {
        super.baseMethod();
        System.out.println("This is an overridden method in DerivedClass");
    }

    public void derivedMethod() {
        System.out.println("This is a method from DerivedClass");
        System.out.println("Derived var: " + derivedVar);
        baseMethod();
    }

    // Demonstrate lambda expression
    public void performOperation(int x, int y) {
        Operation addition = (a, b) -> a + b;
        System.out.println("Result of addition: " + addition.operate(x, y));
    }

    @FunctionalInterface
    interface Operation {
        int operate(int a, int b);
    }
}