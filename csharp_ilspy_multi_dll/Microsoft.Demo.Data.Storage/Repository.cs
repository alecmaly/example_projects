// ILSpy-generated
using Microsoft.Demo.Data.Common;

namespace Microsoft.Demo.Data.Storage
{
    public class Repository
    {
        public string Load(string key)
        {
            string normalized = Utilities.Normalize(key);
            if (Globals.RequestCount > 1000)
            {
                Globals.LastError = "throttled";
                return "throttled";
            }
            return "record:" + normalized;
        }

        public void Reset()
        {
            Globals.RequestCount = 0;
            Globals.LastError = string.Empty;
        }
    }
}
