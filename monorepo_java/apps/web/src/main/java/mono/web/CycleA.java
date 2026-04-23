package mono.web;

// C1.a — Java cycle. Same package, no .java forward-decl needed.
public class CycleA {
    private final String name;
    private CycleB child;                        // C1.a.type_ref → CycleB

    public CycleA(String name) { this.name = name; }

    public CycleB spawnBravo() { return new CycleB(name + "/b"); }
    public String describe()   { return "CycleA(" + name + ")"; }

    public static String kickOff() {
        CycleA a = new CycleA("root");
        CycleB b = a.spawnBravo();
        return b.bounceToAlpha();
    }
}
