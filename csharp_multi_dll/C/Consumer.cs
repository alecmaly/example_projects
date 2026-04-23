using System;
using A.Types;   // cross-dir — A lives in ../A
using B.Logic;   // cross-dir — B lives in ../B

namespace C.App
{
    public static class Consumer
    {
        public static void Run()
        {
            var w = new Widget("alpha", 3);               // A
            var proc = new Processor();                    // B
            var processed = proc.Process(w);               // B writes Registry.Count
            Console.WriteLine(processed);
            Console.WriteLine($"Registry.Count = {Registry.Count}"); // A READ from C
            proc.BulkReset();                               // B→A write
            Console.WriteLine($"Registry.Count after reset = {Registry.Peek()}");
        }

        public static void Main() => Run();
    }
}
