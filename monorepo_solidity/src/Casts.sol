// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Casts {
    // 1. Explicit numeric truncation.
    function narrow(uint256 a) external pure returns (uint8) {
        return uint8(a);                           // truncating
    }

    // 2. Signed <-> unsigned.
    function signed(uint256 a) external pure returns (int256) {
        return int256(a);
    }

    // 3. bytes <-> uint.
    function bytesToUint(bytes32 b) external pure returns (uint256) {
        return uint256(b);
    }
    function uintToBytes(uint256 u) external pure returns (bytes32) {
        return bytes32(u);
    }

    // 4. address conversions: address <-> payable <-> uint160.
    function toPayable(address a) external pure returns (address payable) {
        return payable(a);
    }
    function toAddress(uint160 u) external pure returns (address) {
        return address(u);
    }
    function addressToUint(address a) external pure returns (uint160) {
        return uint160(a);
    }

    // 5. Contract-to-address via `address(contract)`.
    function thisAddress() external view returns (address) {
        return address(this);
    }

    // 6. Low-level cast of an address to a specific contract type (interface).
    function asIERC20(address a) external pure returns (address) {
        // The LSP should recognise `IERC20(a)` as a contract-type cast;
        // since we don't have IERC20 here, we demonstrate the shape only.
        return a;   // placeholder — real code would return IERC20(a)
    }

    // 7. enum <-> uint.
    enum Dir { Up, Down, Left, Right }
    function enumFromUint(uint8 n) external pure returns (Dir) {
        require(n <= 3, "out of range");
        return Dir(n);
    }
    function uintFromEnum(Dir d) external pure returns (uint8) {
        return uint8(d);
    }
}
