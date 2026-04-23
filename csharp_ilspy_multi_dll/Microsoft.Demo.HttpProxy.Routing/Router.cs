// ILSpy-generated
using Microsoft.Demo.Data.Common;
using Microsoft.Demo.Data.Storage;

namespace Microsoft.Demo.HttpProxy.Routing
{
    public class Router
    {
        private readonly Repository repo = new Repository();

        public string Route(string path)
        {
            if (Globals.LastError.Length > 0)
            {
                return "error:" + Globals.LastError;
            }
            return repo.Load(path);
        }
    }
}
