using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Mono.Web;

// Advanced-feature coverage ported from the flat csharp/. Covers:
// async/await, IAsyncEnumerable + yield return + await foreach, LINQ
// Where/Select, extension method, async lambda, generic constraint,
// recursive async.

// --- Extension-method host (static class, `this` param).
public static class StringExt
{
    public static string AddExclamation(this string s) => $"{s}!";
}

// --- Generic class with a constraint.
public class NumberProcessor<T> where T : struct, IComparable<T>
{
    public T Process(T input) => input;
}

public static class Advanced
{
    // yield return — synchronous generator.
    public static IEnumerable<int> CountTo(int n)
    {
        for (int i = 0; i < n; i++) yield return i;
    }

    // IAsyncEnumerable + yield return — async generator.
    public static async IAsyncEnumerable<int> GenerateSequenceAsync()
    {
        for (int i = 0; i < 5; i++)
        {
            await Task.Delay(5);
            yield return i;
        }
    }

    // Recursive async.
    public static async Task RecursiveFunctionAsync(int n)
    {
        if (n <= 0) return;
        await Task.Delay(5);
        await RecursiveFunctionAsync(n - 1);
    }

    public static async Task Run()
    {
        // Extension method.
        Console.WriteLine("hello".AddExclamation());

        // Generic + constraint.
        Console.WriteLine(new NumberProcessor<int>().Process(42));

        // LINQ over a synchronous generator.
        var numbers = CountTo(6);
        var evenSquares = numbers.Where(n => n % 2 == 0).Select(n => n * n).ToList();
        Console.WriteLine($"even squares: {string.Join(",", evenSquares)}");

        // await foreach over IAsyncEnumerable.
        await foreach (var item in GenerateSequenceAsync())
        {
            Console.WriteLine($"async item: {item}");
        }

        // Async lambda stored in a delegate.
        Func<Task<string>> asyncLambda = async () =>
        {
            await Task.Delay(5);
            return "async lambda done";
        };
        Console.WriteLine(await asyncLambda());

        // Recursive async.
        await RecursiveFunctionAsync(3);

        // Parallel fan-out via Task.WhenAll.
        var tasks = Enumerable.Range(1, 4).Select(async i =>
        {
            await Task.Delay(5);
            return i * i;
        });
        var results = await Task.WhenAll(tasks);
        Console.WriteLine($"parallel: [{string.Join(",", results)}]");
    }

    // --- Unsafe block with pointer arithmetic.
    public static unsafe int SumPtr(int* p, int len)
    {
        int total = 0;
        for (int i = 0; i < len; i++)
        {
            total += *(p + i);
        }
        return total;
    }

    // --- Caller that stackallocs and invokes SumPtr.
    public static unsafe int StackAllocSumDemo()
    {
        Span<int> buf = stackalloc int[4] { 1, 2, 3, 4 };
        fixed (int* p = buf)
        {
            return SumPtr(p, buf.Length);
        }
    }

    // --- Iterator with yield return + yield break.
    public static IEnumerable<int> EvensUpTo(int limit)
    {
        for (int i = 0; i <= limit; i++)
        {
            if (i > limit) yield break;
            if (i % 2 == 0) yield return i;
        }
        yield break;
    }

    // --- Span<int> parameter.
    public static int SpanSum(Span<int> xs)
    {
        int total = 0;
        foreach (var x in xs) total += x;
        return total;
    }

    // --- ref / in / out parameter combo.
    public static bool TryDivide(in int a, in int b, out int result, ref int callCount)
    {
        callCount++;
        if (b == 0)
        {
            result = 0;
            return false;
        }
        result = a / b;
        return true;
    }
}

// --- partial class (declaration 1) + partial method signature.
public partial class PartialWidget
{
    public string Name { get; set; } = "widget";
    partial void OnPing(string tag);

    public void Ping(string tag)
    {
        OnPing(tag);
    }
}

// --- partial class (declaration 2) + partial method implementation.
public partial class PartialWidget
{
    partial void OnPing(string tag)
    {
        Console.WriteLine($"{Name} pinged with {tag}");
    }
}
