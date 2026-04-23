package com.example.app;

import com.example.lib.Registry;

/* Obfuscated helper — typical JADX output. */
public class a {
    public static int m0(android.content.Context ctx) {
        Registry.count = Registry.count + 1; // cross-artifact WRITE
        return Registry.count;
    }
}
