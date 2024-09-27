import asyncio
from typing import Generator
import time

MODULE1_GLOBAL = "I'm global in module1"

class BaseClass:
    def __init__(self):
        self.base_var = "I'm a base class variable"

    async def base_method(self):
        print("This is a method from BaseClass")
        print(f"Base var: {self.base_var}")
        await asyncio.sleep(0.1)  # Simulate some async work

class DerivedClass(BaseClass):
    def __init__(self):
        super().__init__()
        self.derived_var = "I'm a derived class variable"

    async def derived_method(self):
        print("This is a method from DerivedClass")
        print(f"Derived var: {self.derived_var}")
        await self.base_method()

    async def base_method(self):
        await super().base_method()
        print("This is an overridden method in DerivedClass")

async def function1():
    local_var = "I'm local to function1"
    print("This is function1 from module1")
    print(f"Local var in function1: {local_var}")
    print(f"Accessing global: {MODULE1_GLOBAL}")

    base_obj = BaseClass()
    derived_obj = DerivedClass()
    
    await base_obj.base_method()
    await derived_obj.derived_method()

# Demonstrate nested functions and closures
def outer_function():
    outer_var = "I'm in the outer function"
    
    def inner_function():
        inner_var = "I'm in the inner function"
        print(f"Inner accessing outer: {outer_var}")
        print(f"Inner local: {inner_var}")
    
    inner_function()
    print(f"Outer local: {outer_var}")

# Decorator
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time:.2f} seconds to execute.")
        return result
    return wrapper

# Context manager
class CustomContextManager:
    def __enter__(self):
        print("Entering the context")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Exiting the context")

# Error handling
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

# Generator
def fibonacci_generator(n: int) -> Generator[int, None, None]:
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

if __name__ == "__main__":
    outer_function()