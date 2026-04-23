package mono.web;

// Plain class import.
import mono.shared.User;
// Wildcard import — brings every class in the package into scope.
import mono.shared.*;
// Static member import.
import static mono.shared.Util.formatUser;
// Static wildcard — every public static member of Clamp.
import static mono.utils.Clamp.*;

public class Main {
    public static void main(String[] args) throws Exception {
        User u = new User(1, "alice");
        Role role = Role.DEFAULT;           // via wildcard
        System.out.println(formatUser(u) + " " + role);
        System.out.println("tag=" + TAG + " clamped=" + clamp(42, 0, 10));

        // Ported coverage from the flat java/ fixture.
        Features.runDemo();
        Scopes.runScopeDemo();
        Imports.demo();
        Advanced.runDemo();
        Casts.runCastsDemo();

        // T1 transitive chain — read via the deepest package's alias;
        // LSP must trace through Deep.VALUE_ALIAS → Middle.MIDDLE_VALUE → Origin.ORIGIN_VALUE.
        System.out.println("transitive: " + mono.chain.Deep.VALUE_ALIAS);

        // Cycle: CycleA ↔ CycleB.
        System.out.println("cycle: " + CycleA.kickOff());
    }
}
