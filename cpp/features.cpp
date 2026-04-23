// C++ feature coverage: templates, lambdas, RAII, inheritance, STL,
// constexpr, auto, range-for, structured bindings, smart pointers.
#include <algorithm>
#include <iostream>
#include <memory>
#include <optional>
#include <string>
#include <variant>
#include <vector>

namespace features {

// Function template.
template <typename T>
T clamp(T n, T lo, T hi) { return std::max(lo, std::min(hi, n)); }

// Class template with constraints-via-SFINAE (pre-C++20).
template <typename T>
class Box {
    T value;
  public:
    explicit Box(T v) : value(std::move(v)) {}
    const T& get() const { return value; }
};

// Inheritance + virtual dispatch + override.
class Animal {
  public:
    virtual ~Animal() = default;
    virtual std::string speak() const = 0;            // pure virtual
};

class Dog : public Animal {
    std::string breed;
  public:
    Dog(std::string b) : breed(std::move(b)) {}
    std::string speak() const override {
        return "woof (" + breed + ")";
    }
};

// Multiple inheritance — FlyingFish derives from both Swimmer and Flyer.
class Swimmer {
  public:
    virtual ~Swimmer() = default;
    virtual std::string swim() const { return "swim"; }
};

class Flyer {
  public:
    virtual ~Flyer() = default;
    virtual std::string fly() const { return "fly"; }
};

class FlyingFish : public Swimmer, public Flyer {
  public:
    std::string swim() const override { return "flying-fish swim"; }
    std::string fly()  const override { return "flying-fish fly"; }
};

// Operator overloading.
struct Vec2 {
    double x, y;
    Vec2 operator+(const Vec2& o) const { return {x + o.x, y + o.y}; }
    double dot(const Vec2& o) const { return x * o.x + y * o.y; }
};

// constexpr function — compile-time evaluation.
constexpr int fib(int n) { return n < 2 ? n : fib(n - 1) + fib(n - 2); }

// Lambda + capture + STL algorithm.
std::vector<int> even_squares(const std::vector<int>& xs) {
    std::vector<int> out;
    std::for_each(xs.begin(), xs.end(), [&out](int n) {
        if (n % 2 == 0) out.push_back(n * n);
    });
    return out;
}

// std::variant — tagged union.
using Shape = std::variant<double, std::pair<double, double>>;
double area(const Shape& s) {
    if (auto* r = std::get_if<double>(&s)) return 3.14159 * *r * *r;
    if (auto* p = std::get_if<std::pair<double,double>>(&s)) return p->first * p->second;
    return 0;
}

// std::optional — nullable return.
std::optional<int> parse_port(const std::string& s) {
    try { return std::stoi(s); } catch (...) { return std::nullopt; }
}

// RAII resource wrapper.
class FileHandle {
    std::string path;
  public:
    FileHandle(std::string p) : path(std::move(p)) {}
    ~FileHandle() { /* close */ }
    FileHandle(const FileHandle&) = delete;           // non-copyable
    FileHandle(FileHandle&&) = default;               // movable
};

void run_feature_demo() {
    // Template deduction.
    auto v = clamp(42, 0, 10);
    Box<std::string> boxed("hi");

    // Smart pointer + polymorphism.
    std::unique_ptr<Animal> a = std::make_unique<Dog>("collie");
    std::cout << a->speak() << "\n";

    // Multiple inheritance — dispatch on each base's virtual.
    FlyingFish ff;
    Swimmer& s_ref = ff;
    Flyer&   f_ref = ff;
    std::cout << s_ref.swim() << " / " << f_ref.fly() << "\n";

    // Structured binding.
    std::vector<std::pair<int, int>> pairs = { {1, 2}, {3, 4} };
    for (const auto& [first, second] : pairs) {
        std::cout << first << "," << second << "\n";
    }

    // constexpr.
    constexpr int k = fib(10);
    std::cout << "fib(10) = " << k << "\n";

    // Lambda + STL.
    auto sq = even_squares({1, 2, 3, 4, 5});
    std::cout << "even squares: ";
    for (int n : sq) std::cout << n << " ";
    std::cout << "\n";

    // Variant + optional.
    Shape s{2.5};
    std::cout << "area=" << area(s) << "\n";
    if (auto p = parse_port("8080")) std::cout << "port=" << *p << "\n";

    // RAII move.
    FileHandle f("/tmp/x");
    FileHandle g = std::move(f);
    (void)boxed; (void)v; (void)g;
}

} // namespace features
