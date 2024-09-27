using System;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace CSharpExample
{
    public class Class1
    {
        private string privateVar;
        public static string StaticVar { get; } = "I'm a static variable in Class1";

        public Class1()
        {
            privateVar = "I'm private";
        }

        public async Task Method1Async()
        {
            Console.WriteLine("This is Method1 from Class1");
            await PrivateMethodAsync();
        }

        private async Task PrivateMethodAsync()
        {
            Console.WriteLine("This is a private method in Class1");
            Console.WriteLine($"Private var: {privateVar}");
            Console.WriteLine($"Static var: {StaticVar}");
            await Task.Delay(100); // Simulate some async work
        }

        // Demonstrate generic method
        public T ProcessData<T>(T input) where T : IComparable<T>
        {
            Console.WriteLine($"Processing data of type {typeof(T).Name}");
            return input;
        }

        // Demonstrate yield return
        public IEnumerable<int> GenerateSequence(int count)
        {
            for (int i = 0; i < count; i++)
            {
                yield return i;
            }
        }

        // Demonstrate extension method
        public static class Extensions
        {
            public static string AddExclamation(this string str)
            {
                return $"{str}!";
            }
        }
    }
}