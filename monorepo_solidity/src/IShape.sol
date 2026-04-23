// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IShape {
    function area() external view returns (uint256);
}

abstract contract Animal {
    function speak() public pure virtual returns (string memory);
    function describe() public pure returns (string memory) {
        return speak();
    }
}

contract CircleContract is IShape {
    uint256 public r;
    error BadRadius(uint256 given);

    constructor(uint256 _r) {
        if (_r == 0) revert BadRadius(_r);
        r = _r;
    }

    // `override` — implements the interface function (required by 0.8.x).
    function area() external view override returns (uint256) {
        return 314 * r * r / 100;
    }
}

// Concrete subclass of the abstract Animal — exercises `virtual` / `override`.
contract Cat is Animal {
    // `virtual override` — overrides Animal.speak and allows further override.
    function speak() public pure virtual override returns (string memory) {
        return "meow";
    }
}

// Virtual + override chain (multi-level): Cat -> PoliteCat overrides speak again.
contract PoliteCat is Cat {
    function speak() public pure override returns (string memory) {
        return "meow, please";
    }
}
