SUBMODULE_GLOBAL = "I'm global in submodule"

def sub_function():
    sub_local = "I'm local to sub_function"
    print("This is sub_function from submodule")
    print(f"Submodule global: {SUBMODULE_GLOBAL}")
    print(f"Sub local: {sub_local}")

# Demonstrate lambda functions and higher-order functions
add = lambda x, y: x + y
multiply = lambda x, y: x * y

def operate(func, x, y):
    return func(x, y)

if __name__ == "__main__":
    print(f"Add result: {operate(add, 5, 3)}")
    print(f"Multiply result: {operate(multiply, 5, 3)}")