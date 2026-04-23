// ILSpy-generated
using System;
using Microsoft.Demo.Data.Common;
using Microsoft.Demo.HttpProxy.Handler;
using Microsoft.Demo.HttpProxy.ModernHandler;

namespace Microsoft.Demo.FrontEnd
{
    internal static class Program
    {
        private static readonly Handler handler = new Handler();
        private static readonly ModernHandler modernHandler = new ModernHandler();

        private static void Main(string[] args)
        {
            string path = args.Length > 0 ? args[0] : "/";
            string legacyResult = handler.HandleRequest(path);
            string modernResult = modernHandler.HandleRequest(path);
            Console.WriteLine("legacy=" + legacyResult);
            Console.WriteLine("modern=" + modernResult);
            Console.WriteLine("requests=" + Globals.RequestCount);
        }
    }
}
