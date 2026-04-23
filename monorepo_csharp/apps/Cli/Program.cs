using Mono.Shared;

namespace Mono.Cli;

public static class Program
{
    public static void Main() =>
        System.Console.WriteLine(Util.FormatUser(new User(99, "cli-user")));
}
