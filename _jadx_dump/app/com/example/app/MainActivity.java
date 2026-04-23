package com.example.app;

import com.example.lib.Widget;
import com.example.lib.Registry;
import com.example.app.R;

/* JADX-style decompiled: anon inner, lambda bridge, obfuscated helper call. */
public class MainActivity extends android.app.Activity {
    private static String TAG = "MainActivity";

    /* synthetic */ static int f10xabc = 0;

    public void onCreate(android.os.Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        /* anonymous inner class */
        findViewById(R.id.btn).setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                Registry.count++; // cross-artifact WRITE
                a.m0(v.getContext());
            }
        });
    }

    /* JADX lambda bridge */
    public static /* synthetic */ Widget lambda$update$0(Widget w) {
        return new Widget(w.name + "!", w.weight * 2);
    }

    private void update() {
        Widget w = new Widget("alpha", 3);
        Widget w2 = MainActivity$Lambda$0.get(w);
        f10xabc++;
    }
}
