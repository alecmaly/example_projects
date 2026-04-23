// Exhaustive C++ #include / using catalogue.

// 1. System header (angle brackets) — searches system include paths only.
#include <string>
#include <vector>

// 2. Local header (double quotes) — searches CWD first.
#include "src/lib.hpp"

// 3. Macro-defined include path (legal but rare).
#define WHICH <cstdio>
#include WHICH

// 4. using declaration (single name).
using std::string;

// 5. using directive (whole namespace).
using namespace std;

// 6. namespace alias.
namespace fs_alias = std;

// 7. Type alias (modern "using X = ...").
using WideString = std::wstring;

// 8. typedef (classic).
typedef std::vector<int> IntVec;

namespace imports_demo {

void run() {
    string s = "hello";
    vector<int> xs;
    IntVec ys;
    WideString w;
    fs_alias::printf("via macro include path\n");
    lib::hello_from_lib();
    (void)s; (void)xs; (void)ys; (void)w;
}

} // namespace imports_demo
