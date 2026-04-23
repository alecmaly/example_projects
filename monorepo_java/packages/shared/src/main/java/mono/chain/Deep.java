package mono.chain;

// T1.deep — hop 2. Aliased re-export through a class field.
public final class Deep {
    private Deep() {}
    public static final String VALUE_ALIAS = Middle.MIDDLE_VALUE;    // T1.deep.reexport
}
