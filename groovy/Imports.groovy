package com.example

// 1. Single-type import.
import java.util.ArrayList

// 2. Wildcard import.
import java.util.*

// 3. Static member import.
import static java.lang.Math.PI

// 4. Static wildcard.
import static java.lang.Math.*

// 5. Aliased import — Groovy-specific `as` clause.
import groovy.transform.ToString as TS

// 6. Nested-type import.
import java.util.Map.Entry

@TS(includeNames = true)
class ImportsDemo {
    static void run() {
        ArrayList<Integer> xs = new ArrayList<>()
        HashMap<String, Integer> m = new HashMap<>()
        Entry<String, Integer> e = null
        double v = PI + sqrt(2) + max(1, 2)
        println "xs=$xs m=$m e=$e v=$v"
    }
}
