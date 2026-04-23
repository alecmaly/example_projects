// ILSpy-generated
extern alias sharedlib;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using sharedlib::Shared.Types;

namespace CoreLib
{
    [CompilerGenerated]
    internal sealed class Processor
    {
        // Fields written by the ctor
        internal readonly List<Widget> items;
        internal string status;

        [CompilerGenerated]
        private sealed class <>c__DisplayClass0_0
        {
            public int threshold;
            internal bool <Process>b__0(Widget w) => w.Weight > threshold;
        }

        [CompilerGenerated]
        private sealed class <>c
        {
            public static readonly <>c <>9 = new <>c();
            internal Widget <Process>b__1_0(Widget w) => new Widget(w.Name + "!", w.Weight);
        }

        public Processor()
        {
            items = new List<Widget>();
            status = "initial";
        }

        public IEnumerable<Widget> Process(int threshold)
        {
            <>c__DisplayClass0_0 CS$<>8__locals0 = new <>c__DisplayClass0_0 { threshold = threshold };
            Registry.Count++; // cross-assembly WRITE of Shared.Types.Registry.Count
            return items.Where(CS$<>8__locals0.<Process>b__0).Select(<>c.<>9.<Process>b__1_0);
        }

        // Synthesized by the compiler for boxed async state machine
        [AsyncStateMachine(typeof(Processor))]
        public void Reset()
        {
            Registry.Count = 0;
            status = "reset";
        }
    }

    // Compiler-generated "backing store" class ILSpy commonly renders:
    [CompilerGenerated]
    internal static class <PrivateImplementationDetails>
    {
        public static int $$method0x6000001 = 0;
    }
}
