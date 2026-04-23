// Plain namespace import.
using Mono.Utils;
using System.Threading.Tasks;
// using static — brings every static member of the class into file scope.
using static Mono.Shared.Util;
// Namespace alias.
using SharedNs = Mono.Shared;

namespace Mono.Web;

public static class Program
{
    public static async Task Main()
    {
        // User / Role resolved via GlobalUsings.cs (global using Mono.Shared).
        var u = new User(1, "alice");
        var role = Defaults.DEFAULT_ROLE;

        // Hello() is imported via `using static Mono.Shared.Util`.
        Console.WriteLine($"{FormatUser(u)} {role}");
        Console.WriteLine(Hello("world"));

        // Access via alias.
        Console.WriteLine(SharedNs.Util.FormatUser(u));

        // Fully-qualified reference to Utils.
        Console.WriteLine($"tag={Clamp.TAG} clamped={Clamp.Between(42, 0, 10)}");

        // Ported coverage from the flat csharp/ fixture.
        FeatureSamples.Run();
        Scopes.Run();
        Imports.Demo();

        // Advanced coverage: async/await, LINQ, yield, extension, IAsyncEnumerable.
        await Advanced.Run();
        Casts.Run();

        // T1 transitive chain — Deep.VALUE_ALIAS must resolve to Origin.ORIGIN_VALUE.
        Console.WriteLine($"transitive: {Mono.Shared.Chain.Deep.VALUE_ALIAS}");

        // Cycle: CycleA ↔ CycleB.
        Console.WriteLine($"cycle: {CycleA.KickOff()}");
    }
}
