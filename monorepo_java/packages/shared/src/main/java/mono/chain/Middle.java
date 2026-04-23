package mono.chain;

// T1.middle — hop 1. Re-exposes the origin value as a constant on this class.
public final class Middle {
    private Middle() {}
    public static final String MIDDLE_VALUE = Origin.ORIGIN_VALUE;   // T1.middle.reexport
}
