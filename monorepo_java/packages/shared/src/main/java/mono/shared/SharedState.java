package mono.shared;

public class SharedState {
    public static String status = "initial";

    @Audited(reason = "cross-file mutator")
    public static void setStatus(String s) { status = s; }
}
