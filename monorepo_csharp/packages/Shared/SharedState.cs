using System;

namespace Mono.Shared;

[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public class AuditedAttribute : Attribute
{
    public string Reason { get; }
    public AuditedAttribute(string reason) { Reason = reason; }
}

public delegate void StatusChangedHandler(string newStatus);

public class StatusBroker
{
    public event StatusChangedHandler? OnStatusChanged;
    public static string SharedStatus = "initial";
    public void Publish(string s)
    {
        SharedStatus = s;
        OnStatusChanged?.Invoke(s);
    }
}

public interface IShape
{
    double Area();
    string Name { get; }
}

public abstract class Animal
{
    public abstract string Speak();
    public virtual string Describe() => $"I am a {GetType().Name} that says {Speak()}";
}

public class CircleShape : IShape
{
    private double _r;
    public CircleShape(double r) { _r = r; }
    public double Area() => Math.PI * _r * _r;
    public string Name => "Circle";
}

public class Dog : Animal
{
    public override string Speak() => "woof";
}
