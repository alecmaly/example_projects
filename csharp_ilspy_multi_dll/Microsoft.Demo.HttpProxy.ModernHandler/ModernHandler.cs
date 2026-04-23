// ILSpy-generated
using System;
using System.Linq;
using Microsoft.Demo.Data.Common;
using Microsoft.Demo.HttpProxy.Routing;

namespace Microsoft.Demo.HttpProxy.ModernHandler;

public class ModernHandler
{
	private readonly Router router = new Router();

	public string HandleRequest(string requestPath)
	{
		Func<string, string> transform = (string p) => router.Route(p);
		string result = transform(requestPath);
		if (Globals.LastError.Length > 0)
		{
			return "error:" + Globals.LastError;
		}
		return result;
	}

	public string[] HandleBatch(string[] paths)
	{
		return paths.Where((string p) => p != null).Select((string p) => router.Route(p)).ToArray();
	}
}
