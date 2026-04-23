package mono.web;

import java.lang.reflect.Method;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import mono.shared.SharedState;

// Advanced-feature coverage ported from the flat java/. Covers:
// CompletableFuture, Stream API + collectors, reflection, raw Thread +
// Runnable, @FunctionalInterface, method overloading, @Override +
// extends chain, lambda with checked-exception wrapping.

public class Advanced {

    @FunctionalInterface
    interface Operation {
        int operate(int a, int b);
    }

    // Method overloading — int / String variants.
    private static int add(int a, int b) { return a + b; }
    private static String add(String a, String b) { return a + b; }

    // Generic method — `<T extends Number>` bound.
    private static <T extends Number> double sum(List<T> numbers) {
        return numbers.stream()
            .mapToDouble(Number::doubleValue)
            .sum();
    }

    // Classic extends + @Override chain.
    public static class AnimalBase {
        protected String name;
        public AnimalBase(String name) { this.name = name; }
        public String speak() { return name + " makes a sound"; }
    }

    public static class DogJ extends AnimalBase {
        private final String breed;
        public DogJ(String name, String breed) {
            super(name);
            this.breed = breed;
        }
        @Override
        public String speak() {
            return super.speak() + " (woof, " + breed + ")";
        }
    }

    public static void runDemo() throws Exception {
        // Method overloading.
        System.out.println("add int = " + add(5, 3));
        System.out.println("add str = " + add("hello ", "world"));

        // Streams + collectors.
        List<Integer> numbers = List.of(1, 2, 3, 4, 5);
        List<Integer> evenSquares = numbers.stream()
            .filter(n -> n % 2 == 0)
            .map(n -> n * n)
            .collect(Collectors.toList());
        System.out.println("even squares: " + evenSquares);

        // Generic method call.
        System.out.println("sum: " + sum(numbers));

        // Stream + String.join
        String joined = IntStream.range(0, 5)
            .mapToObj(i -> "item" + i)
            .collect(Collectors.joining(","));
        System.out.println("joined: " + joined);

        // Functional interface usage.
        Operation addition = (a, b) -> a + b;
        System.out.println("op: " + addition.operate(7, 8));

        // CompletableFuture — async.
        CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
            try { Thread.sleep(5); } catch (InterruptedException e) {}
            return "async result";
        });
        System.out.println("future: " + future.get());

        // Raw Thread + Runnable.
        AtomicInteger counter = new AtomicInteger();
        Thread t = new Thread(() -> counter.incrementAndGet());
        t.start();
        t.join();
        System.out.println("threaded counter: " + counter.get());

        // Reflection — invoke SharedState.setStatus via Method.
        Method m = SharedState.class.getDeclaredMethod("setStatus", String.class);
        m.invoke(null, "via-reflection");
        System.out.println("reflected status: " + SharedState.status);

        // Inheritance chain.
        AnimalBase a = new DogJ("Rex", "collie");
        System.out.println(a.speak());
    }

    // --- Sealed interface + record permits (Java 17+).
    public sealed interface Payment permits CardPayment, CashPayment, CheckPayment {}
    public record CardPayment(String last4, double amount) implements Payment {}
    public record CashPayment(double amount) implements Payment {}
    public record CheckPayment(String checkNumber, double amount) implements Payment {}

    // --- Switch expression with arrow labels, yield, and pattern matching.
    public static String describePayment(Payment p) {
        return switch (p) {
            case CardPayment c -> "card " + c.last4();
            case CashPayment cash -> "cash " + cash.amount();
            case CheckPayment chk -> {
                String prefix = "check#";
                yield prefix + chk.checkNumber() + " for " + chk.amount();
            }
        };
    }

    // --- Text block (multi-line string literal).
    public static final String PAYMENT_JSON_TEMPLATE = """
        {
          "type": "card",
          "last4": "0000",
          "amount": 0.0,
          "metadata": {
            "source": "fixture",
            "note": "multi-line text block"
          }
        }
        """;

    // --- Method reference used in a stream pipeline.
    public static List<String> shoutAll(List<String> list) {
        return list.stream()
            .map(String::toUpperCase)
            .collect(Collectors.toList());
    }

    // --- Minimal AutoCloseable helper for try-with-resources.
    public static class CloseableGreeter implements AutoCloseable {
        private final String who;
        public CloseableGreeter(String who) { this.who = who; }
        public String greet() { return "hello, " + who; }
        @Override
        public void close() { System.out.println("closing greeter for " + who); }
    }

    public static String tryWithResourcesDemo() throws Exception {
        try (CloseableGreeter g = new CloseableGreeter("world")) {
            return g.greet();
        }
    }
}
