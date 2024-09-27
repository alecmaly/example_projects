import asyncio
import module1
from module2 import function2, MODULE2_CONSTANT
from subpackage import submodule
from typing import List, Callable
import random

global_var = "I'm global in main"

async def main():
    local_var = "I'm local to main"
    print(global_var)
    print(local_var)
    print(f"Imported constant: {MODULE2_CONSTANT}")
    
    base_obj = module1.BaseClass()
    derived_obj = module1.DerivedClass()
    
    await base_obj.base_method()
    await derived_obj.base_method()
    await derived_obj.derived_method()
    
    await module1.function1()
    await function2()
    await submodule.sub_function()
    await recursive_function(5)
    
    # Accessing module-level variables
    print(f"Module1 global: {module1.MODULE1_GLOBAL}")
    print(f"Submodule global: {submodule.SUBMODULE_GLOBAL}")

    # Demonstrate decorators
    @module1.timing_decorator
    def slow_function():
        import time
        time.sleep(1)
        print("Slow function finished")

    slow_function()

    # Demonstrate context manager
    with module1.CustomContextManager() as ctx:
        print(f"Inside context manager: {ctx}")

    # Demonstrate error handling
    try:
        result = module1.divide(10, 0)
    except ZeroDivisionError as e:
        print(f"Caught exception: {e}")

    # Demonstrate higher-order function
    numbers = [1, 2, 3, 4, 5]
    squared_numbers = list(map(lambda x: x**2, numbers))
    print(f"Squared numbers: {squared_numbers}")

    # Demonstrate generator
    for value in module1.fibonacci_generator(10):
        print(f"Fibonacci value: {value}")

    # Using a standard library function
    random_number = random.randint(1, 100)
    print(f"Random number: {random_number}")

async def recursive_function(n: int):
    if n <= 0:
        return
    print(f"Recursion level: {n}")
    await asyncio.sleep(0.1)  # Simulate some async work
    await recursive_function(n - 1)

def test():
    print("test")
    test2()

def test2():
    print("test2")

if __name__ == "__main__":
    asyncio.run(main())