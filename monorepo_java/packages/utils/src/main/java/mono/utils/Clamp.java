package mono.utils;

public final class Clamp {
    public static final String TAG = "utils";

    private Clamp() {}

    public static int clamp(int n, int lo, int hi) {
        return Math.max(lo, Math.min(hi, n));
    }
}
