#include <string>
using namespace std;
namespace ns {
    class Greeter {
      public:
        string prefix = "hi";
        string greet(const string& name) { return prefix + " " + name; }
    };
    string helper() { return "x"; }
}
using MyG = ns::Greeter;

// Forward declarations for the expanded coverage files.
namespace features { void run_feature_demo(); }
namespace imports_demo { void run(); }
void run_scope_demo_cpp();

int main() {
    MyG g;
    ns::helper();
    auto r = g.greet("world").size();
    features::run_feature_demo();
    imports_demo::run();
    run_scope_demo_cpp();
    return static_cast<int>(r);
}
