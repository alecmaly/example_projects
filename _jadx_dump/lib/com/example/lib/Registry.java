package com.example.lib;

/* Cross-artifact mutable state — written from ../app. */
public final class Registry {
    public static int count = 0;

    public static void reset() {
        count = 0;
    }

    /* synthetic bridge method */
    static /* synthetic */ int access$000() {
        return count;
    }
}
