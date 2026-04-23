package mono.web;

import java.util.List;
import java.util.ArrayList;

public class Casts {

    static class Base {}
    static class Derived extends Base { public String extra() { return "derived"; } }

    // 1. Primitive narrowing cast.
    static int narrowCast(long l) { return (int) l; }

    // 2. Primitive widening (implicit).
    static long widen(int i)      { return i; }

    // 3. Reference downcast.
    static String downcast(Object o) { return (String) o; }

    // 4. instanceof check + downcast.
    static String legacyInstanceof(Object o) {
        if (o instanceof String) return ((String) o).toUpperCase();
        return "?";
    }

    // 5. Pattern-matching instanceof (Java 16+).
    static String patternInstanceof(Object o) {
        if (o instanceof String s) return s.toUpperCase();
        if (o instanceof Integer n) return String.valueOf(n * 2);
        return "other";
    }

    // 6. Autoboxing / unboxing.
    static void boxing() {
        Integer boxed = 42;              // int → Integer
        int primitive = boxed;           // Integer → int
        List<Integer> xs = new ArrayList<>();
        xs.add(1);                       // autobox
    }

    // 7. Generic wildcard + cast.
    @SuppressWarnings("unchecked")
    static <T> List<T> unsafeList(Object o) {
        return (List<T>) o;              // unchecked; raises warning
    }

    // 8. Numeric parsing / formatting.
    static void parsing() {
        int n = Integer.parseInt("42");
        double d = Double.parseDouble("3.14");
        String s = String.valueOf(n);
        System.out.println(n + " " + d + " " + s);
    }

    // 9. Downcast with runtime check.
    static String tryDownCast(Base b) {
        if (b instanceof Derived d) return d.extra();
        return "base";
    }

    public static void runCastsDemo() {
        System.out.println(narrowCast(1_000_000_000_000L));
        System.out.println(widen(3));
        System.out.println(downcast("hi"));
        System.out.println(legacyInstanceof("low"));
        System.out.println(patternInstanceof(42));
        boxing();
        List<String> xs = unsafeList(new ArrayList<String>());
        xs.add("a");
        parsing();
        System.out.println(tryDownCast(new Derived()));
    }
}
