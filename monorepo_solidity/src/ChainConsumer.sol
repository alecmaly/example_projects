// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import { Deep } from "./chain/Deep.sol";

contract ChainConsumer {
    // LSP must follow Deep.valueAlias → Middle.middleValue → Origin.originValue.
    function transitive() external pure returns (string memory) {
        return Deep.valueAlias();
    }
}
