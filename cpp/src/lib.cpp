#include "lib.hpp"
#include <iostream>

namespace lib {
    void hello_from_lib() { std::cout << "from lib " << constant() << "\n"; }
}
