using System;
using A.Types; // cross-dir reference — no csproj links these

namespace B.Logic
{
    public class Processor
    {
        public Widget Process(Widget w)
        {
            // WRITE to A.Types.Registry.Count from a different directory
            Registry.Count += 1;
            return new Widget(w.Name.ToUpper(), w.Weight * 2);
        }

        public void BulkReset() => Registry.Reset(); // cross-dir method call that also writes
    }
}
