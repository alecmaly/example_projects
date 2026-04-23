#include "cycle.hpp"

namespace cycle {

std::shared_ptr<Bravo> Alpha::spawnBravo() {
    return std::make_shared<Bravo>(name_ + "/b");
}

std::string Bravo::bounceToAlpha() const {
    return Alpha("bounce-from-" + tag_).describe();
}

std::string kickOff() {
    Alpha a("root");
    auto b = a.spawnBravo();
    return b->bounceToAlpha();
}

} // namespace cycle
