using System;
using System.Collections.Generic;

namespace Mono.Shared;

// Record (C# 9+) — ported from the flat csharp/Features.cs so the
// monorepo retains positional-record + `with`-expression coverage.
public record Money(long Amount, string Currency)
{
    public Money Add(Money other) =>
        Currency == other.Currency
            ? this with { Amount = Amount + other.Amount }
            : throw new InvalidOperationException();
}

// Record struct (C# 10+)
public readonly record struct Point(double X, double Y);

[Flags]
public enum Permission
{
    None  = 0,
    Read  = 1 << 0,
    Write = 1 << 1,
    Admin = 1 << 2,
    All   = Read | Write | Admin,
}

public static class FeatureSamples
{
    public static bool TryParseDollars(string s, out long cents)
    {
        cents = 0;
        if (string.IsNullOrEmpty(s) || !s.StartsWith("$")) return false;
        return long.TryParse(s[1..], out cents);
    }

    public static void Swap<T>(ref T a, ref T b) { (a, b) = (b, a); }

    public static double Distance(in Point a, in Point b) =>
        Math.Sqrt(Math.Pow(a.X - b.X, 2) + Math.Pow(a.Y - b.Y, 2));

    public static (int min, int max, double avg) Stats(IEnumerable<int> xs)
    {
        int min = int.MaxValue, max = int.MinValue, count = 0;
        long sum = 0;
        foreach (var x in xs) { min = Math.Min(min, x); max = Math.Max(max, x); sum += x; count++; }
        return (min, max, (double)sum / Math.Max(count, 1));
    }

    public static string Describe(object? o) => o switch
    {
        null                       => "null",
        int i when i < 0           => $"negative int {i}",
        int i                      => $"non-negative int {i}",
        string { Length: 0 }       => "empty string",
        string s                   => $"string '{s}'",
        Point { X: 0, Y: 0 }       => "origin",
        Point p                    => $"point {p}",
        IEnumerable<int>           => $"int sequence",
        _                          => $"other: {o.GetType().Name}"
    };

    public static void Run()
    {
        if (TryParseDollars("$1234", out var cents)) Console.WriteLine($"cents={cents}");
        int a = 1, b = 2;
        Swap(ref a, ref b);
        Console.WriteLine($"after swap a={a} b={b}");
        var p1 = new Point(0, 0); var p2 = new Point(3, 4);
        Console.WriteLine($"dist={Distance(in p1, in p2)}");

        var (min, max, avg) = Stats(new[] { 1, 2, 3, 4, 5 });
        Console.WriteLine($"min={min} max={max} avg={avg}");

        var perms = Permission.Read | Permission.Write;
        Console.WriteLine($"flags={perms} has Admin? {perms.HasFlag(Permission.Admin)}");

        Console.WriteLine(Describe(-3));
        Console.WriteLine(Describe("hello"));
        Console.WriteLine(Describe(new Point(0, 0)));
    }
}
