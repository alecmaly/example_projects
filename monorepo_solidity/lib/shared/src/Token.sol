// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import { IERC20Like } from "./IERC20Like.sol";

contract Token is IERC20Like {
    mapping(address => uint256) private _balances;
    uint256 public totalSupply;

    error Insufficient(address who, uint256 needed, uint256 have);

    function mint(address to, uint256 amount) external {
        _balances[to] += amount;
        totalSupply   += amount;
    }

    function balanceOf(address who) external view returns (uint256) {
        return _balances[who];
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        if (_balances[msg.sender] < amount) {
            revert Insufficient(msg.sender, amount, _balances[msg.sender]);
        }
        _balances[msg.sender] -= amount;
        _balances[to]         += amount;
        return true;
    }
}
