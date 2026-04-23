// C++20 feature coverage fixture. Parser-only — not expected to link or run.
// Covers: concepts, coroutines, ranges pipelines, and auto + trailing return.

#include <concepts>
#include <coroutine>
#include <ranges>
#include <type_traits>
#include <utility>

namespace cpp20_features {

// --- Concepts ---
template<typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template<Numeric T>
T twice(T x) {
    return x + x;
}

// Alt spelling: trailing `requires` clause.
template<typename T>
    requires Numeric<T>
T triple(T x) {
    return x * 3;
}

// --- Coroutines ---
// Minimal generator type: enough promise shape for the parser to chew on.
struct Generator {
    struct promise_type {
        int current_value{};

        Generator get_return_object() {
            return Generator{
                std::coroutine_handle<promise_type>::from_promise(*this)
            };
        }
        std::suspend_always initial_suspend() noexcept { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        std::suspend_always yield_value(int v) noexcept {
            current_value = v;
            return {};
        }
        void return_void() noexcept {}
        void unhandled_exception() { std::terminate(); }
    };

    std::coroutine_handle<promise_type> handle;

    explicit Generator(std::coroutine_handle<promise_type> h) : handle(h) {}
    Generator(const Generator&) = delete;
    Generator(Generator&& o) noexcept : handle(std::exchange(o.handle, {})) {}
    ~Generator() { if (handle) handle.destroy(); }

    bool next() {
        if (!handle || handle.done()) return false;
        handle.resume();
        return !handle.done();
    }
    int value() const { return handle.promise().current_value; }
};

// Coroutine producer that uses co_yield and co_return.
Generator count_up_to(int n) {
    for (int i = 0; i < n; ++i) {
        co_yield i;
    }
    co_return;
}

// --- Ranges pipeline ---
auto even_squares_under_ten() {
    return std::views::iota(1, 10)
         | std::views::filter([](int i) { return i % 2 == 0; })
         | std::views::transform([](int i) { return i * i; });
}

// --- auto return with trailing return type ---
auto combine(int a, int b) -> decltype(a + b) {
    return a + b;
}

} // namespace cpp20_features
