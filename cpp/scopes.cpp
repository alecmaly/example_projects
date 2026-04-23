// Labeled scope test cases for C++. See SCOPE_TEST_SPEC.md.
// N/A: S09 (no aliased-import for SYMBOLS — closest is `using X = Y`),
//      S10 (no re-export syntax — closest is headers transitively including
//      others which is already exercised in imports.cpp).

#include "src/lib.hpp"
#include <iostream>
#include <string>

// ------------------------------------------------------- S04 def / S05 write
int module_var = 1;                                // S04.def

void s01_local() {
    int local_a = 123;                             // S01.def
    std::cout << local_a << "\n";                  // S01.read
}

void s02_closure_read() {
    std::string outer_a = "S02.outer";             // S02.outer.def
    auto inner = [&outer_a]() {                    // S02.inner.read
        std::cout << outer_a << "\n";
    };
    inner();
}

int s03_closure_write() {
    int counter = 0;                               // S03.outer.def
    auto bump = [&counter]() { counter++; };       // S03.inner.write
    bump(); bump();
    return counter;                                // S03.outer.read
}

void s05_same_module_write() {
    module_var = 2;                                // S05.write
    std::cout << module_var << "\n";               // S05.read
}

int s06_cross_read() {
    return lib::constant();                        // S06.read (cross-TU)
}

void s08_shadowing() {
    int module_var = 999;                          // S08.shadow.def
    std::cout << module_var << "\n";               // S08.shadow.read
}

class ScopeBase {
  public:
    static int static_x;                           // S12.static.def / S13.base.def
    int x;                                         // S11.instance.def
    ScopeBase(int v) : x(v) {}
    int read_instance(int x) const {
        return x + this->x;                        // S11.param.read + S11.instance.read
    }
};
int ScopeBase::static_x = 1;

class ScopeDerived : public ScopeBase {
  public:
    ScopeDerived() : ScopeBase(5) {}
    int read_inherited() const {
        return static_x;                           // S13.derived.read
    }
};

namespace scope_ns {
    struct Widget {                                // S14.Widget.def
        std::string label;
        Widget(std::string l) : label(std::move(l)) {}
    };
}

std::string s14_qualified() {
    scope_ns::Widget w("hi");
    return w.label;                                // S14.read
}

void run_scope_demo_cpp() {
    s01_local();
    s02_closure_read();
    std::cout << s03_closure_write() << "\n";
    s05_same_module_write();
    std::cout << s06_cross_read() << "\n";
    s08_shadowing();
    ScopeBase b(42);
    std::cout << b.read_instance(100) << "\n";
    ScopeDerived d;
    std::cout << d.read_inherited() << "\n";
    std::cout << s14_qualified() << "\n";
}
