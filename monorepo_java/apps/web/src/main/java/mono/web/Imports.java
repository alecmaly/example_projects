package mono.web;

// 1. Single-type import.
import java.util.ArrayList;
// 2. Wildcard.
import java.util.*;
// 3. Static member import.
import static java.lang.Math.PI;
// 4. Static wildcard.
import static java.lang.Math.*;
// 5. Nested-type import.
import java.util.Map.Entry;
// 6. Cross-workspace-package import.
import mono.shared.Util;
// 7. Static wildcard import from sibling workspace pkg.
import static mono.utils.Clamp.*;

public class Imports {
    public static void demo() {
        ArrayList<Integer> xs = new ArrayList<>();
        HashMap<String, Integer> m = new HashMap<>();
        Entry<String, Integer> e = null;
        double x = PI + sqrt(2.0) + max(1, 2);
        int c = clamp(42, 0, 10);
        System.out.println(xs.size() + m.size() + (int) x + (e == null ? 0 : 1)
            + Util.hello("x").length() + c);
    }
}
