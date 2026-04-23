using System;

namespace Mono.Web;

public static class Casts
{
    // 1. Numeric explicit cast.
    static int Narrow(long l) => (int) l;

    // 2. `as` — null on failure (ref types only).
    static string AsDowncast(object o) => o as string ?? "<not string>";

    // 3. `is` type-test.
    static bool IsString(object o) => o is string;

    // 4. Pattern match with type check.
    static string Describe(object o) => o switch {
        string s when s.Length > 3 => $"long string {s}",
        string s                   => $"short string {s}",
        int i                      => $"int {i}",
        _                          => "other",
    };

    // 5. Pattern-matching `is T t`.
    static string IsPattern(object o) {
        if (o is int n) return $"int={n}";
        return "other";
    }

    // 6. checked / unchecked arithmetic casts.
    static int OverflowSafe(long big) {
        try { return checked((int) big); }
        catch (OverflowException) { return -1; }
    }

    // 7. User-defined implicit & explicit conversion operators.
    public readonly struct Temperature
    {
        public double Celsius { get; }
        public Temperature(double c) { Celsius = c; }
        public static implicit operator double(Temperature t) => t.Celsius;
        public static explicit operator Temperature(double c) => new Temperature(c);
    }

    // 8. Convert helper class.
    static int ConvertDemo(string s) => Convert.ToInt32(s);

    // 9. Boxing / unboxing.
    static void Boxing() {
        int i = 42;
        object o = i;                 // boxing
        int back = (int) o;           // unboxing
        Console.WriteLine(back);
    }

    // 10. Nullable-value cast via `GetValueOrDefault` / null-coalescing.
    static int NullableCast(int? n) => n.GetValueOrDefault(-1);

    public static void Run() {
        Console.WriteLine(Narrow(99_999_999_999L));
        Console.WriteLine(AsDowncast("hi"));
        Console.WriteLine(IsString(3.14));
        Console.WriteLine(Describe("verylong"));
        Console.WriteLine(IsPattern(42));
        Console.WriteLine(OverflowSafe(long.MaxValue));
        Temperature t = (Temperature) 25.0;
        double d = t;                  // implicit
        Console.WriteLine($"{t.Celsius}C={d}");
        Console.WriteLine(ConvertDemo("123"));
        Boxing();
        Console.WriteLine(NullableCast(null));
    }
}
