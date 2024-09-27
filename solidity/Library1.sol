// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

library Library1 {
    event Log(string message);

    function function1() public {
        emit Log("This is function1 from Library1");
        internalFunction();
    }

    function internalFunction() internal {
        emit Log("This is an internal function in Library1");
    }
}