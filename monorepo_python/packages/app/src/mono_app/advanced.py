"""Python advanced-feature coverage ported from the flat python/ fixture.

Covers: asyncio async/await, context manager protocol, generator functions,
explicit ZeroDivisionError handling, classic single-inheritance chain with
super(). These were implicit in the flat main.py / module1.py and didn't
make it into the original monorepo port.
"""
from __future__ import annotations

import asyncio
from contextlib import contextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Generator, NotRequired, TypedDict


# ----------------------------------------------------------------- async/await
async def _nap(ms: int) -> int:
    await asyncio.sleep(ms / 1000)
    return ms


async def run_async_demo() -> None:
    # Awaiting a coroutine.
    n = await _nap(10)
    print(f"napped {n}ms")
    # asyncio.gather for concurrent fan-out.
    results = await asyncio.gather(_nap(5), _nap(5), _nap(5))
    print(f"gathered {results}")


# ----------------------------------------------------------- context manager
class CustomContextManager:
    """Protocol-style context manager via __enter__ / __exit__."""

    def __enter__(self):
        print("Entering the context")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Exiting the context")


@contextmanager
def brackets(name: str) -> Generator[str, None, None]:
    """Decorator-based context manager — different shape, same protocol."""
    print(f"[{name}>")
    try:
        yield name
    finally:
        print(f"<{name}]")


# ------------------------------------------------------------------- generators
def fibonacci_generator(n: int) -> Generator[int, None, None]:
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


def counting_gen(start: int = 0):
    # Generator that receives values via .send()
    while True:
        bump = yield start
        start += bump or 1


# -------------------------------------------------------- classic inheritance
class Animal:
    """Base class exercising super() chain + __init__."""
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return f"{self.name} makes a sound"


class Dog(Animal):
    def __init__(self, name: str, breed: str) -> None:
        super().__init__(name)             # super() delegation
        self.breed = breed

    def speak(self) -> str:
        # super().speak() reaches up the MRO
        return f"{super().speak()} (woof, {self.breed})"


# ------------------------------------------------------------------- exceptions
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


def run_exception_demo() -> None:
    try:
        divide(10, 0)
    except ZeroDivisionError as e:
        print(f"Caught: {e}")
    else:
        print("no exception")
    finally:
        print("finally")


# ------------------------------------------------------------------- entry
def run_advanced_demo() -> None:
    asyncio.run(run_async_demo())

    with CustomContextManager() as ctx:
        print("inside:", ctx)

    with brackets("demo") as tag:
        print("tag:", tag)

    for v in fibonacci_generator(6):
        print("fib:", v)

    gen = counting_gen(100)
    next(gen)
    gen.send(5)
    next(gen)

    d = Dog("Rex", "collie")
    print(d.speak())

    run_exception_demo()


# -------------------------------------------------- structural pattern matching
@dataclass
class Point:
    """Small dataclass used in class patterns below."""
    x: int
    y: int


def classify(value):
    # match/case (PEP 634) — mapping, sequence, class, wildcard patterns.
    match value:
        case {"status": 200, "body": body}:
            return f"ok: {body}"
        case [head, *tail]:
            return f"seq head={head} tail={tail}"
        case Point(x=0, y=0):
            return "origin"
        case _:
            return "unknown"


# ---------------------------------------------------------------- walrus `:=`
def walrus_demo(source: list[int]) -> list[int]:
    # Walrus in a while loop — drain the buffer one value at a time.
    buf = list(source)
    drained: list[int] = []
    while (item := buf.pop() if buf else None) is not None:
        drained.append(item)
    # Walrus in a list comprehension guard — reuse the computed value.
    squared_big = [y for n in source if (y := n * n) > 10]
    return drained + squared_big


# ------------------------------------------------------------- async generator
async def astream_async() -> AsyncIterator[int]:
    """Async generator yielding a few values with awaits in between."""
    for i in range(3):
        await asyncio.sleep(0)
        yield i


# ------------------------------------------------------------------- TypedDict
class UserTD(TypedDict):
    id: int
    name: str
    email: NotRequired[str]


# -------------------------------------------------------------------- metaclass
class RegistryMeta(type):
    registry: list[type] = []

    def __new__(cls, name, bases, dct):
        new_cls = super().__new__(cls, name, bases, dct)
        if name != "Foo" or True:
            RegistryMeta.registry.append(new_cls)
        return new_cls


class Foo(metaclass=RegistryMeta):
    def hello(self) -> str:
        return "foo"
