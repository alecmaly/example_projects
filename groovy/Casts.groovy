package com.example

// Groovy cast / coercion catalogue.

class Casts {
    // 1. `as` operator — Groovy's primary cast.
    static void asOperator() {
        def s = "42" as Integer
        def l = "3.14" as Double
        def arr = [1, 2, 3] as Integer[]
        println "$s $l ${arr.class.simpleName}"
    }

    // 2. asType — method form.
    static void asTypeMethod() {
        def n = "42".asType(Integer)
        println "asType $n"
    }

    // 3. C-style cast — works for primitives.
    static void cStyle() {
        def n = (int) 3.7
        println "c-style $n"    // 3 (truncating)
    }

    // 4. Duck typing — implicit coercion via GDK.
    static void duckTyping() {
        def list = [1, 2, 3]
        def s = list as String  // "[1, 2, 3]"
        println s
    }

    // 5. instanceof check.
    static boolean isCollection(obj) { obj instanceof Collection }

    // 6. GString <-> String.
    static void gstring() {
        def name = "world"
        def g = "hello, $name"     // GString
        def s = g.toString()       // plain String
        println "${g.class.simpleName} -> ${s.class.simpleName}"
    }

    // 7. List → Map via collectEntries.
    static void listToMap() {
        def m = [[1, 'a'], [2, 'b']].collectEntries { [it[0], it[1]] }
        println m
    }

    static void run() {
        asOperator()
        asTypeMethod()
        cStyle()
        duckTyping()
        println isCollection([])
        gstring()
        listToMap()
    }
}
