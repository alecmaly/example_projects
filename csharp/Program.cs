using System;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Linq;

namespace CSharpExample
{
    class Program
    {
        static string globalVar = "I'm global in Program";

        static async Task Main(string[] args)
        {
            string localVar = "I'm local to Main";
            Console.WriteLine(globalVar);
            Console.WriteLine(localVar);
            Console.WriteLine($"Imported constant: {Class2.Class2Constant}");

            var baseObj = new BaseClass();
            var derivedObj = new DerivedClass();

            await baseObj.BaseMethodAsync();
            await derivedObj.BaseMethodAsync();
            await derivedObj.DerivedMethodAsync();

            var genericObj = new GenericClass<int>(42);
            genericObj.DisplayValue();

            await Class2.Function1Async();
            await RecursiveFunctionAsync(5);

            // Accessing class-level variables
            Console.WriteLine($"Class1 static var: {Class1.StaticVar}");
            Console.WriteLine($"Class2 property: {Class2.Class2Property}");

            // Using LINQ and lambda expressions
            var numbers = new List<int> { 1, 2, 3, 4, 5 };
            var evenSquares = numbers.Where(n => n % 2 == 0).Select(n => n * n).ToList();
            Console.WriteLine($"Even squares: {string.Join(", ", evenSquares)}");

            // Using async enumerable
            await foreach (var item in GenerateSequenceAsync())
            {
                Console.WriteLine($"Generated: {item}");
            }

            // Demonstrate function overloading
            Console.WriteLine(Add(5, 3));
            Console.WriteLine(Add(5.5, 3.3));
            Console.WriteLine(Add("Hello", "World"));

            // Demonstrate generic constraints
            var numberProcessor = new NumberProcessor<int>();
            Console.WriteLine(numberProcessor.Process(10));

            // Demonstrate async lambda
            Func<Task> asyncLambda = async () =>
            {
                await Task.Delay(100);
                Console.WriteLine("Async lambda executed");
            };
            await asyncLambda();
        }

        static async Task RecursiveFunctionAsync(int n)
        {
            if (n <= 0) return;
            Console.WriteLine($"Recursion level: {n}");
            await Task.Delay(100); // Simulate some async work
            await RecursiveFunctionAsync(n - 1);
        }

        static async IAsyncEnumerable<int> GenerateSequenceAsync()
        {
            for (int i = 0; i < 5; i++)
            {
                await Task.Delay(100);
                yield return i;
            }
        }

        // Function overloading
        static int Add(int a, int b) => a + b;
        static double Add(double a, double b) => a + b;
        static string Add(string a, string b) => a + b;
    }

    class GenericClass<T>
    {
        private T value;

        public GenericClass(T value)
        {
            this.value = value;
        }

        public void DisplayValue()
        {
            Console.WriteLine($"Generic value: {value}");
        }
    }

    class BaseClass
    {
        protected string baseVar = "I'm a base class variable";

        public virtual async Task BaseMethodAsync()
        {
            Console.WriteLine("This is a method from BaseClass");
            Console.WriteLine($"Base var: {baseVar}");
            await Task.Delay(100);
        }
    }

    class DerivedClass : BaseClass
    {
        private string derivedVar = "I'm a derived class variable";

        public override async Task BaseMethodAsync()
        {
            await base.BaseMethodAsync();
            Console.WriteLine("This is an overridden method in DerivedClass");
        }

        public async Task DerivedMethodAsync()
        {
            Console.WriteLine("This is a method from DerivedClass");
            Console.WriteLine($"Derived var: {derivedVar}");
            await BaseMethodAsync();
        }
    }

    // Generic class with constraint
    class NumberProcessor<T> where T : struct, IComparable<T>
    {
        public T Process(T input) => input;
    }
}