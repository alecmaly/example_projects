// 1. Plain namespace using.
using System;
// 3. using static.
using static System.Math;
// 4. Namespace alias.
using SysColls = System.Collections.Generic;
// 5. Type alias.
using StringList = System.Collections.Generic.List<string>;
// 6. Cross-workspace-package usings.
using Mono.Shared;
using static Mono.Utils.Clamp;

namespace Mono.Web;

public static class Imports
{
    public static void Demo()
    {
        Console.WriteLine("hello");
        Console.WriteLine(PI + Sqrt(2) + Max(1, 2));
        var q = new SysColls.Queue<int>();
        var names = new StringList();
        var u = new User(1, "alice");
        Console.WriteLine($"{Util.FormatUser(u)} q={q.Count} n={names.Count} c={Between(42, 0, 10)}");
    }
}
