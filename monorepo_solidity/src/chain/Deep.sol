// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import { Middle } from "./Middle.sol";

library Deep {
    function valueAlias() internal pure returns (string memory) {
        return Middle.middleValue();                          // T1.deep.reexport
    }
}
