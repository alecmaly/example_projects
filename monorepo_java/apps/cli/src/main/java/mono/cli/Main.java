package mono.cli;

import mono.shared.User;
import mono.shared.Util;

public class Main {
    public static void main(String[] args) {
        System.out.println(Util.formatUser(new User(99, "cli-user")));
    }
}
