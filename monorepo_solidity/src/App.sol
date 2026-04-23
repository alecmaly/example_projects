// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// 1. Whole-file import via remapping ("@shared" -> lib/shared/src).
import "@shared/Token.sol";
// 2. Named import.
import { IERC20Like } from "@shared/IERC20Like.sol";
// 3. Aliased named import.
import { IERC20Like as IERC20 } from "@shared/IERC20Like.sol";
// 4. Module-level alias — every symbol in the file becomes a member of M.
import "@utils/Math.sol" as M;
// 5. Relative-path import between sibling files under `src/`.
import { Helper } from "./Helper.sol";

contract App {
    Token public immutable token;

    constructor(Token t) { token = t; }

    function withdraw(address to, uint256 amount) external {
        token.transfer(to, amount);
    }

    function clampedBalance(address who) external view returns (uint256) {
        return M.Math.clamp(token.balanceOf(who), 0, 1_000_000);
    }

    function isIerc20(address who) external view returns (bool) {
        IERC20 t = IERC20(who);              // aliased-interface use
        return t.balanceOf(who) >= 0;
    }

    function helper() external pure returns (uint256) {
        return Helper.compute();
    }
}
