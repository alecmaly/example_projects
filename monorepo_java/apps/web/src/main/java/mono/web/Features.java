package mono.web;

import java.util.List;
import java.util.ArrayList;

public class Features {
    public enum Priority {
        LOW(1), MEDIUM(5), HIGH(10);
        private final int weight;
        Priority(int weight) { this.weight = weight; }
        public int weight() { return weight; }
        public static Priority fromWeight(int w) {
            for (Priority p : values()) if (p.weight == w) return p;
            throw new IllegalArgumentException("bad weight " + w);
        }
    }

    public record Money(long amount, String currency) {
        public Money {
            if (currency == null) throw new IllegalArgumentException();
        }
        public Money add(Money other) {
            if (!currency.equals(other.currency)) throw new IllegalArgumentException();
            return new Money(amount + other.amount, currency);
        }
    }

    static double sumOfList(List<? extends Number> list) {
        double s = 0;
        for (Number n : list) s += n.doubleValue();
        return s;
    }

    static void fillWithZeros(List<? super Integer> list, int n) {
        for (int i = 0; i < n; i++) list.add(0);
    }

    public static class Resource implements AutoCloseable {
        private final String name;
        public Resource(String name) { this.name = name; System.out.println("open " + name); }
        public void use() { System.out.println("use " + name); }
        @Override public void close() { System.out.println("close " + name); }
    }

    static String describe(Priority p) {
        return switch (p) {
            case LOW -> "take your time";
            case MEDIUM -> "soon please";
            case HIGH -> "drop everything";
        };
    }

    public static void runDemo() {
        System.out.println("priority weight = " + Priority.HIGH.weight());
        System.out.println("from weight 5 = " + Priority.fromWeight(5));
        System.out.println("description = " + describe(Priority.MEDIUM));

        Money m1 = new Money(100, "USD");
        Money m2 = new Money(50, "USD");
        System.out.println("sum = " + m1.add(m2));

        List<Integer> ints = List.of(1, 2, 3);
        System.out.println("sum = " + sumOfList(ints));
        List<Number> nums = new ArrayList<>();
        fillWithZeros(nums, 3);
        System.out.println("nums = " + nums);

        try (Resource a = new Resource("a"); Resource b = new Resource("b")) {
            a.use();
            b.use();
        }
    }
}
