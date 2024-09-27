MODULE2_CONSTANT = "I'm a constant in module2"
_module2_private = "I'm a private variable in module2"

def function2():
    print("This is function2 from module2")
    print(f"Accessing module constant: {MODULE2_CONSTANT}")
    internal_function()

def internal_function():
    internal_var = "I'm local to internal_function"
    print("This is an internal function in module2")
    print(f"Internal var: {internal_var}")
    print(f"Accessing private var: {_module2_private}")

# Demonstrate list comprehension and generator expression
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers]
even_squares = (x**2 for x in numbers if x % 2 == 0)

if __name__ == "__main__":
    print(f"Squares: {squares}")
    print(f"Even squares: {list(even_squares)}")