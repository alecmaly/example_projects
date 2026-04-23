#pragma once
#include <string>
#include <memory>

namespace cycle {

class Bravo;                          // forward declaration

class Alpha {
    std::string name_;
    std::shared_ptr<Bravo> child_;    // complete type not yet seen — ok, it's a pointer
  public:
    explicit Alpha(std::string n) : name_(std::move(n)) {}
    std::string describe() const { return "Alpha(" + name_ + ")"; }
    std::shared_ptr<Bravo> spawnBravo();
};

class Bravo : public std::enable_shared_from_this<Bravo> {
    std::string tag_;
    std::weak_ptr<Alpha> owner_;      // weak to break ownership cycle
  public:
    explicit Bravo(std::string t) : tag_(std::move(t)) {}
    std::string bounceToAlpha() const;
};

std::string kickOff();

} // namespace cycle
