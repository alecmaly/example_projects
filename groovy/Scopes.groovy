package com.example

// Labeled scope test cases for Groovy. See SCOPE_TEST_SPEC.md.

class Scopes {
    static String moduleVar = "mod-initial"            // S04.def

    static void s01Local() {
        String localA = "S01.local"                    // S01.def
        println localA                                 // S01.read
    }

    static void s02ClosureRead() {
        String outerA = "S02.outer"                    // S02.outer.def
        def inner = { println outerA }                 // S02.inner.read
        inner()
    }

    static int s03ClosureWrite() {
        int counter = 0                                // S03.outer.def
        def bump = { counter++ }                       // S03.inner.write
        bump(); bump()
        return counter                                 // S03.outer.read
    }

    static void s05SameModuleWrite() {
        moduleVar = "rotated"                          // S05.write
        println moduleVar                              // S05.read
    }

    static void s08Shadowing() {
        String moduleVar = "shadowed"                  // S08.shadow.def
        println moduleVar                              // S08.shadow.read
    }

    static class Base {
        static int staticX = 1                         // S12.static.def / S13.base.def
        int x                                          // S11.instance.def
        Base(int x) { this.x = x }
        int readInstance(int x) {
            return x + this.x                          // S11.param.read + S11.instance.read
        }
    }

    static class Derived extends Base {
        Derived() { super(5) }
        int readInherited() { staticX }                // S13.derived.read

        // Method override — same signature as Base.readInstance.
        @Override
        int readInstance(int x) {
            return super.readInstance(x) * 10          // super call + augment
        }
    }

    static void run() {
        s01Local()
        s02ClosureRead()
        println s03ClosureWrite()
        s05SameModuleWrite()
        s08Shadowing()
        println new Base(42).readInstance(100)
        println new Derived().readInherited()
    }
}
