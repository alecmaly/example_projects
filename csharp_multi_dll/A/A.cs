using System;

namespace A.Types
{
    public class Widget
    {
        public string Name { get; set; }
        public int Weight { get; set; }
        public Widget(string n, int w) { Name = n; Weight = w; }

        public override string ToString() => $"Widget({Name},{Weight})";
    }

    // Cross-artifact mutable state — written by B, read by A and C.
    public static class Registry
    {
        public static int Count = 0;

        public static void Reset() => Count = 0;
        public static int Peek()   => Count;
    }
}
