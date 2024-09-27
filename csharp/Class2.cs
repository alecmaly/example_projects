using System;
using System.Threading.Tasks;
using System.Linq;

namespace CSharpExample
{
    public static class Class2
    {
        public const string Class2Constant = "I'm a constant in Class2";
        public static string Class2Property { get; } = "I'm a static property in Class2";

        public static async Task Function1Async()
        {
            Console.WriteLine("This is Function1 from Class2");
            Console.WriteLine($"Accessing class constant: {Class2Constant}");
            await InternalFunctionAsync();
        }

        private static async Task InternalFunctionAsync()
        {
            string localVar = "I'm local to InternalFunction";
            Console.WriteLine("This is an internal function in Class2");
            Console.WriteLine($"Local var: {localVar}");
            Console.WriteLine($"Class property: {Class2Property}");
            await Task.Delay(100); // Simulate some async work
        }

        // Demonstrate LINQ
        public static void DemonstrateLinq()
        {
            var numbers = Enumerable.Range(1, 10);
            var evenSquares = numbers.Where(n => n % 2 == 0).Select(n => n * n).ToList();
            Console.WriteLine($"Even squares: {string.Join(", ", evenSquares)}");
        }

        // Demonstrate pattern matching
        public static void PatternMatchingExample(object obj)
        {
            switch (obj)
            {
                case int i when i > 0:
                    Console.WriteLine($"Positive integer: {i}");
                    break;
                case string s:
                    Console.WriteLine($"String of length {s.Length}");
                    break;
                case null:
                    Console.WriteLine("Null object");
                    break;
                default:
                    Console.WriteLine("Unknown type");
                    break;
            }
        }
    }
}