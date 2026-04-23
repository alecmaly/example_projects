// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Exhaustive Solidity import forms — monorepo edition.

// 1. Plain file import via remapping.
import "@shared/Token.sol";
// 2. Named import (symbol list).
import { IERC20Like } from "@shared/IERC20Like.sol";
// 3. Aliased named import.
import { IERC20Like as IERC20 } from "@shared/IERC20Like.sol";
// 4. Module-level alias — every top-level symbol becomes a member of M.
import "@utils/Math.sol" as M;
// 5. Import-all-as (whole-file alias).
import * as FeaturesAll from "./Features.sol";
// 6. Relative-path import.
import { Helper } from "./Helper.sol";

contract ImportsDemo {
    function demo() external returns (uint256) {
        Token t = new Token();
        IERC20 asIerc20 = IERC20(address(t));
        uint256 clamped = M.Math.clamp(t.balanceOf(address(this)), 0, 100);
        // Sanity-touch the wildcard-aliased module:
        FeaturesAll.FeaturesContract f = FeaturesAll.FeaturesContract(address(0));
        f;
        asIerc20;
        return Helper.compute() + clamped;
    }
}
