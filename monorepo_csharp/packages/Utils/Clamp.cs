namespace Mono.Utils;

public static class Clamp
{
    public const string TAG = "utils";

    public static int Between(int n, int lo, int hi) =>
        System.Math.Max(lo, System.Math.Min(hi, n));
}
