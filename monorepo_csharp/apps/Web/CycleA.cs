namespace Mono.Web;

public class CycleA
{
    private readonly string _name;
    public CycleB? Child { get; set; }                        // C1.a.type_ref → CycleB

    public CycleA(string name) { _name = name; }

    public CycleB SpawnBravo() => new CycleB(_name + "/b");
    public string Describe()   => $"CycleA({_name})";

    public static string KickOff()
    {
        var a = new CycleA("root");
        var b = a.SpawnBravo();
        return b.BounceToAlpha();
    }
}

public class CycleB
{
    private readonly string _tag;
    public CycleA? Owner { get; set; }                        // C1.b.type_ref → CycleA

    public CycleB(string tag) { _tag = tag; }

    public string BounceToAlpha() => new CycleA($"bounce-from-{_tag}").Describe();
}
