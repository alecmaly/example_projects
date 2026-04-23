// ILSpy-generated
using System;
using System.Runtime.CompilerServices;
using Microsoft.Demo.Data.Common;
using Microsoft.Demo.HttpProxy.Routing;

namespace Microsoft.Demo.HttpProxy.Handler
{
    public class Handler
    {
        private readonly Router router = new Router();

        public string HandleRequest(string requestPath)
        {
            <>c__DisplayClass0_0 CS$<>8__locals0 = new <>c__DisplayClass0_0 { <>4__this = this };
            Func<string, string> transform = CS$<>8__locals0.<HandleRequest>b__0;
            string result = transform(requestPath);
            if (Globals.LastError.Length > 0)
            {
                return "error:" + Globals.LastError;
            }
            return result;
        }

        [CompilerGenerated]
        private sealed class <>c__DisplayClass0_0
        {
            public Handler <>4__this;

            internal string <HandleRequest>b__0(string p)
            {
                return <>4__this.router.Route(p);
            }
        }
    }
}
