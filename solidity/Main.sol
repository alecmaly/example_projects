// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./Contract1.sol";
import "./Library1.sol";

contract Main {
    string public globalVar = "I'm global";
    uint256 private constant SOME_CONSTANT = 42;

    event Log(string message);
    event RecursionLevel(uint256 level);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not the owner");
        _;
    }

    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function main() public {
        string memory localVar = "I'm local to main";
        emit Log(globalVar);
        emit Log(localVar);

        Contract1 obj = new Contract1();
        obj.method1();

        Library1.function1();
        recursiveFunction(5);

        // Demonstrate use of modifiers
        restrictedFunction();

        // Demonstrate use of try/catch
        try obj.mayRevert() {
            emit Log("Function did not revert");
        } catch Error(string memory reason) {
            emit Log(string(abi.encodePacked("Function reverted with reason: ", reason)));
        } catch (bytes memory lowLevelData) {
            emit Log("Function reverted with no reason");
        }
    }

    function recursiveFunction(uint n) public {
        if (n == 0) return;
        emit RecursionLevel(n);
        recursiveFunction(n - 1);
    }

    function restrictedFunction() public onlyOwner {
        emit Log("This function can only be called by the owner");
    }

    // Payable function example
    function deposit() public payable {
        emit Log(string(abi.encodePacked("Received ", uint2str(msg.value), " wei")));
    }

    // Assembly block example
    function uint2str(uint _i) internal pure returns (string memory _uintAsString) {
        if (_i == 0) {
            return "0";
        }
        uint j = _i;
        uint len;
        while (j != 0) {
            len++;
            j /= 10;
        }
        bytes memory bstr = new bytes(len);
        uint k = len;
        while (_i != 0) {
            k = k-1;
            uint8 temp = (48 + uint8(_i - _i / 10 * 10));
            bytes1 b1 = bytes1(temp);
            bstr[k] = b1;
            _i /= 10;
        }
        return string(bstr);
    }

    // Fallback function
    fallback() external payable {
        emit Log("Fallback function called");
    }

    // Receive function
    receive() external payable {
        emit Log("Receive function called");
    }
}