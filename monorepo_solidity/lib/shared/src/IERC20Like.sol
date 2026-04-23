// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20Like {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address who) external view returns (uint256);
}
