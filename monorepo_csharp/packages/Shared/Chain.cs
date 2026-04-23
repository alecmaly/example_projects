namespace Mono.Shared.Chain;

// T1.origin — definition lives here.
public static class Origin
{
    public const string ORIGIN_VALUE = "T1.origin";         // T1.origin.def
}

// T1.middle — re-exposes origin's value as its own constant.
public static class Middle
{
    public const string MIDDLE_VALUE = Origin.ORIGIN_VALUE; // T1.middle.reexport
}

// T1.deep — final hop, renamed.
public static class Deep
{
    public const string VALUE_ALIAS = Middle.MIDDLE_VALUE;  // T1.deep.reexport
}
