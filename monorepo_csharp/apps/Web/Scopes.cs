using System;
using Mono.Shared;
using Mono.Shared.ScopesNs;

// Type alias (C# feature) — doubles as S09.def.
using StatusAlias = Mono.Shared.StatusBroker;

namespace Mono.Web;

public static class Scopes
{
    public static string ModuleVar = "mod-initial";   // S04.def

    public static void S01Local()
    {
        string localA = "S01.local";                   // S01.def
        Console.WriteLine(localA);                     // S01.read
    }

    public static void S02ClosureRead()
    {
        string outerA = "S02.outer";                   // S02.outer.def
        Action a = () => Console.WriteLine(outerA);    // S02.inner.read
        a();
    }

    public static int S03ClosureWrite()
    {
        int counter = 0;                               // S03.outer.def
        Action bump = () => { counter++; };            // S03.inner.write
        bump(); bump();
        return counter;                                // S03.outer.read
    }

    public static void S05SameModuleWrite()
    {
        ModuleVar = "rotated";                         // S05.write
        Console.WriteLine(ModuleVar);                  // S05.read
    }

    public static string S06CrossRead()  => StatusBroker.SharedStatus;  // S06.read
    public static void   S07CrossWrite() { StatusBroker.SharedStatus = "S07"; } // S07.write

    public static void S08Shadowing()
    {
        string ModuleVar = "shadowed";                 // S08.shadow.def
        Console.WriteLine(ModuleVar);                  // S08.shadow.read
    }

    public static void S09AliasedImport()
    {
        StatusAlias.SharedStatus = "via-alias";        // S09.read (via type alias)
    }

    public class Base
    {
        public static int StaticX = 1;                 // S12.static.def / S13.base.def
        public int X;                                  // S11.instance.def
        public Base(int x) { X = x; }
        public int ReadInstance(int x) => x + this.X;  // S11.param.read + S11.instance.read
    }

    public class Derived : Base
    {
        public Derived() : base(5) { }
        public int ReadInherited() => StaticX;         // S13.derived.read
    }

    public static string S14Qualified() =>
        new Widget("hi").Label;                        // S14.read

    public static void Run()
    {
        S01Local();
        S02ClosureRead();
        Console.WriteLine(S03ClosureWrite());
        S05SameModuleWrite();
        Console.WriteLine(S06CrossRead());
        S07CrossWrite();
        S08Shadowing();
        S09AliasedImport();
        Console.WriteLine(new Base(42).ReadInstance(100));
        Console.WriteLine(new Derived().ReadInherited());
        Console.WriteLine(S14Qualified());
    }
}
