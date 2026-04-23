package mono.shared;

public final class Util {
    private Util() {}

    public static String formatUser(User u) {
        return u.id() + ":" + u.name();
    }

    public static String hello(String msg) {
        return "hello, " + msg;
    }
}
