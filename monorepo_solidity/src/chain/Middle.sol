// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import { Origin } from "./Origin.sol";

library Middle {
    function middleValue() internal pure returns (string memory) {
        return Origin.originValue();                          // T1.middle.reexport
    }
}
