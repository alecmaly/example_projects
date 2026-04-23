// ILSpy-generated
using System;

namespace Microsoft.Demo.Data.Common
{
    public static class Utilities
    {
        public static string Normalize(string input)
        {
            Globals.RequestCount++;
            if (input == null)
            {
                Globals.LastError = "null input";
                return string.Empty;
            }
            return input.Trim().ToLowerInvariant();
        }
    }
}
