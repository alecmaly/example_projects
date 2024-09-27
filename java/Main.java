import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;

public class Main {
    private static String globalVar = "I'm global";

    public static void main(String[] args) throws Exception {
        String localVar = "I'm local to main";
        System.out.println(globalVar);
        System.out.println(localVar);

        BaseClass baseObj = new BaseClass();
        DerivedClass derivedObj = new DerivedClass();

        baseObj.baseMethod();
        derivedObj.baseMethod();
        derivedObj.derivedMethod();

        Class2.function1();
        recursiveFunction(5);

        // Demonstrate method overloading
        System.out.println(add(5, 3));
        System.out.println(add("Hello", "World"));

        // Demonstrate generic method
        List<Integer> numbers = List.of(1, 2, 3, 4, 5);
        System.out.println("Sum of numbers: " + sum(numbers));

        // Demonstrate lambda and stream
        List<Integer> evenSquares = numbers.stream()
            .filter(n -> n % 2 == 0)
            .map(n -> n * n)
            .collect(Collectors.toList());
        System.out.println("Even squares: " + evenSquares);

        // Demonstrate CompletableFuture
        CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            return "Async operation completed";
        });
        System.out.println(future.get());
    }

    private static void recursiveFunction(int n) {
        if (n <= 0) return;
        System.out.println("Recursion level: " + n);
        recursiveFunction(n - 1);
    }

    // Method overloading
    private static int add(int a, int b) {
        return a + b;
    }

    private static String add(String a, String b) {
        return a + b;
    }

    // Generic method
    private static <T extends Number> double sum(List<T> numbers) {
        return numbers.stream()
            .mapToDouble(Number::doubleValue)
            .sum();
    }
}