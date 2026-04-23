package mono.web;

// Labeled scope test cases for Java — monorepo edition.
// Cross-module refs target the sibling workspace package
// mono.shared (SharedState) and scopes.ns.Widget.
// See SCOPE_TEST_SPEC.md at repo root.

import static java.lang.Math.PI;                       // S09.def
import mono.shared.SharedState;                         // cross-module
import scopes.ns.Widget;                                // S14.import

public class Scopes {
    public static String moduleVar = "mod-initial";     // S04.def

    public static void s01Local() {
        String localA = "S01.local";                    // S01.def
        System.out.println(localA);                     // S01.read
    }

    public static void s02ClosureRead() {
        final String outerA = "S02.outer";              // S02.outer.def
        Runnable r = () -> System.out.println(outerA);  // S02.inner.read
        r.run();
    }

    public static int s03ClosureWrite() {
        int[] counter = { 0 };                           // S03.outer.def
        Runnable bump = () -> { counter[0]++; };         // S03.inner.write
        bump.run(); bump.run();
        return counter[0];                               // S03.outer.read
    }

    public static void s05SameModuleWrite() {
        moduleVar = "rotated";                           // S05.write
        System.out.println(moduleVar);                   // S05.read
    }

    public static String s06CrossRead() {
        return SharedState.status;                       // S06.read
    }

    public static void s07CrossWrite() {
        SharedState.status = "S07";                      // S07.write
    }

    public static void s08Shadowing() {
        String moduleVar = "shadowed";                   // S08.shadow.def
        System.out.println(moduleVar);                   // S08.shadow.read
    }

    public static void s09AliasedImport() {
        System.out.println(PI);                          // S09.read
    }

    public static class Base {
        public static int staticX = 1;                   // S12.static.def + S13.base.def
        public int x;                                    // S11.instance.def

        public Base(int x) { this.x = x; }

        public int readInstance(int x) {
            return x + this.x;                           // S11.param.read + S11.instance.read
        }
    }

    public static class Derived extends Base {
        public Derived() { super(5); }
        public int readInherited() {
            return staticX;                              // S13.derived.read
        }
    }

    public static String s14Qualified() {
        return new Widget("hi").label;                   // S14.read
    }

    public static void runScopeDemo() {
        s01Local();
        s02ClosureRead();
        System.out.println(s03ClosureWrite());
        s05SameModuleWrite();
        System.out.println(s06CrossRead());
        s07CrossWrite();
        s08Shadowing();
        s09AliasedImport();
        System.out.println(new Base(42).readInstance(100));
        System.out.println(new Derived().readInherited());
        System.out.println(s14Qualified());
    }
}
