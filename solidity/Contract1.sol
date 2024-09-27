pragma solidity ^0.8.0;

import "./Library1.sol";

contract Contract1 {
    string private privateVar;
    uint256 public constant CONTRACT_CONSTANT = 100;
    address public owner;

    event Log(string message);
    event MethodCalled(address caller, uint256 value);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not the owner");
        _;
    }

    constructor() {
        privateVar = "I'm private";
        owner = msg.sender;
    }

    function method1() public {
        emit Log("This is method1 from Contract1");
        privateMethod();
        emit MethodCalled(msg.sender, 0);
    }

    function privateMethod() private {
        emit Log("This is a private method in Contract1");
        emit Log(string(abi.encodePacked("Private var: ", privateVar)));
    }

    function mayRevert() public pure {
        require(false, "This function always reverts");
    }

    function useLibrary() public {
        Library1.function1();
    }

    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "Invalid address");
        owner = newOwner;
    }

    receive() external payable {
        emit Log("Ether received");
    }

    fallback() external payable {
        emit Log("Fallback called");
    }
}