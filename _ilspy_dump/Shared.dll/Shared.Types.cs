// ILSpy-generated
using System;
using System.Runtime.CompilerServices;

namespace Shared.Types
{
    public class Widget
    {
        public string Name;
        public int Weight;

        public Widget(string Name, int Weight)
        {
            this.Name = Name;
            this.Weight = Weight;
        }
    }

    // Cross-assembly mutable state.
    public static class Registry
    {
        public static int Count = 0;

        [CompilerGenerated]
        [SpecialName]
        public static int get_Snapshot() => Count;
    }

    // Synthetic nullable wrapper sometimes emitted by the decompiler for <T>? usages
    [CompilerGenerated]
    internal sealed class <>f__AnonymousType0<<Value>j__TPar>
    {
        public <Value>j__TPar Value { get; }
        public <>f__AnonymousType0(<Value>j__TPar Value) { this.Value = Value; }
    }
}
