namespace Mono.Shared;

public static class Util
{
    public static string FormatUser(User u) => $"{u.Id}:{u.Name}";
    public static string Hello(string msg) => $"hello, {msg}";
}
