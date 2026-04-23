// C++ cast catalogue: static_cast / dynamic_cast / const_cast /
// reinterpret_cast, C-style, functional-style, std::bit_cast.

#include <cstdint>
#include <iostream>
#include <memory>
#include <string>
#include <type_traits>

namespace cpp_casts {

// 1. static_cast — checked compile-time conversion (numeric, upcast, etc.).
double widen(int x) { return static_cast<double>(x); }

// 2. dynamic_cast — runtime-checked downcast through virtual hierarchy.
struct Animal { virtual ~Animal() = default; virtual std::string sound() const = 0; };
struct Dog : Animal { std::string sound() const override { return "woof"; } };

std::string try_dog(Animal* a) {
    if (auto d = dynamic_cast<Dog*>(a)) return d->sound();
    return "not a dog";
}

// 3. const_cast — strip constness (use sparingly).
void modify(const int* p) {
    *const_cast<int*>(p) = 42;
}

// 4. reinterpret_cast — bit-level pointer reinterpretation.
uint32_t bits_of(float f) {
    return *reinterpret_cast<uint32_t*>(&f);
}

// 5. C-style cast — combines static + const + reinterpret.
int c_style(double d) { return (int) d; }

// 6. Functional-style cast — same semantics as C-style but written `T(x)`.
int functional(double d) { return int(d); }

// 7. std::bit_cast (C++20) — sanctioned bit-level reinterpret.
#if __cplusplus >= 202002L
#include <bit>
uint32_t bit_cast_demo(float f) { return std::bit_cast<uint32_t>(f); }
#endif

// 8. Implicit conversion via user-defined operator.
struct Temperature {
    double c;
    operator double() const { return c; }   // implicit → double
    explicit operator int() const { return static_cast<int>(c); }  // explicit → int
};

// 9. unique_ptr cast via std::move.
void ownership_demo() {
    std::unique_ptr<Animal> a = std::make_unique<Dog>();
    auto d = std::unique_ptr<Dog>(static_cast<Dog*>(a.release()));
    std::cout << "own: " << d->sound() << "\n";
}

void run_casts_demo_cpp() {
    std::cout << widen(3) << "\n";
    Dog dog;
    std::cout << try_dog(&dog) << "\n";
    int n = 0; modify(&n); std::cout << n << "\n";
    std::cout << std::hex << bits_of(1.0f) << "\n";
    std::cout << std::dec << c_style(3.7) << " " << functional(3.7) << "\n";
#if __cplusplus >= 202002L
    std::cout << std::hex << bit_cast_demo(2.0f) << "\n";
#endif
    Temperature t{25.5};
    double d = t;                // implicit
    int i = static_cast<int>(t); // explicit via operator int
    std::cout << std::dec << d << " " << i << "\n";
    ownership_demo();
}

} // namespace cpp_casts
