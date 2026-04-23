// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Labeled scope test cases for Solidity — monorepo edition.
// Cross-library refs target `@shared/Token.sol` via remapping.

import "./IShape.sol";
import "@shared/Token.sol";

library ToolsScopes {
    function addOne(uint256 a) internal pure returns (uint256) { return a + 1; }
}

contract ScopesBase {
    uint256 public baseVar = 1;                 // S11.instance.def + S13.base.def
    uint256 public constant STATIC_X = 42;      // S12.static.def

    function readInstance(uint256 x) public view returns (uint256) {
        return x + baseVar;                     // S11.param.read + S11.instance.read
    }
}

contract Scopes is ScopesBase {
    using ToolsScopes for uint256;

    uint256 public moduleVar = 10;              // S04.def

    function s01Local() public pure returns (uint256) {
        uint256 localA = 1;                     // S01.def
        return localA;                          // S01.read
    }

    function s05SameModuleWrite() public {
        moduleVar = 99;                         // S05.write
    }

    function s06CrossRead(Scopes other) public view returns (uint256) {
        return other.moduleVar();               // S06.read (public getter)
    }

    function s07CrossWrite(Scopes other) public {
        other.s05SameModuleWrite();             // S07.write (indirect)
    }

    function s13DerivedRead() public view returns (uint256) {
        return baseVar;                         // S13.derived.read
    }

    function libraryForDemo(uint256 x) public pure returns (uint256) {
        return x.addOne();
    }

    function s06CrossTokenRead(Token t, address who) public view returns (uint256) {
        return t.balanceOf(who);                // S06.read — cross-package via remapping
    }
}
