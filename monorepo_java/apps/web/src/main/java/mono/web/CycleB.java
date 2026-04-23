package mono.web;

public class CycleB {
    private final String tag;
    private CycleA owner;                        // C1.b.type_ref → CycleA

    public CycleB(String tag) { this.tag = tag; }

    public String bounceToAlpha() {
        return new CycleA("bounce-from-" + tag).describe();
    }
}
