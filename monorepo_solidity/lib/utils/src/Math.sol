// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

library Math {
    function clamp(uint256 n, uint256 lo, uint256 hi) internal pure returns (uint256) {
        if (n < lo) return lo;
        if (n > hi) return hi;
        return n;
    }
}
