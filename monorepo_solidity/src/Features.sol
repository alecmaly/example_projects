// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Ported from solidity/Features.sol — self-contained.

library SafeMath {
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        unchecked { uint256 c = a + b; require(c >= a, "overflow"); return c; }
    }
}

contract FeaturesContract {
    using SafeMath for uint256;

    enum OrderStatus { Pending, Active, Filled, Cancelled }

    struct Order {
        uint256 id;
        address owner;
        uint256 amount;
        OrderStatus status;
    }

    mapping(uint256 => Order) public orders;
    mapping(address => mapping(OrderStatus => uint256)) public countsByOwnerStatus;

    uint256 public nextId;

    event OrderCreated(uint256 indexed id, address indexed owner, uint256 amount);
    event OrderStatusChanged(uint256 indexed id, OrderStatus oldStatus, OrderStatus newStatus);

    error Unauthorized(address caller, address expected);
    error InvalidTransition(OrderStatus from, OrderStatus to);

    modifier onlyOwnerOf(uint256 id) {
        if (orders[id].owner != msg.sender) revert Unauthorized(msg.sender, orders[id].owner);
        _;
    }

    function create(uint256 amount) external returns (uint256) {
        uint256 id = nextId.add(1);
        nextId = id;
        orders[id] = Order({ id: id, owner: msg.sender, amount: amount, status: OrderStatus.Pending });
        countsByOwnerStatus[msg.sender][OrderStatus.Pending] =
            countsByOwnerStatus[msg.sender][OrderStatus.Pending] + 1;
        emit OrderCreated(id, msg.sender, amount);
        return id;
    }

    function transition(uint256 id, OrderStatus to) external onlyOwnerOf(id) {
        OrderStatus from = orders[id].status;
        if (from == OrderStatus.Filled || from == OrderStatus.Cancelled) revert InvalidTransition(from, to);
        orders[id].status = to;
        countsByOwnerStatus[msg.sender][from] -= 1;
        countsByOwnerStatus[msg.sender][to]   += 1;
        emit OrderStatusChanged(id, from, to);
    }

    function chainId() external view returns (uint256 id) {
        assembly { id := chainid() }
    }
}
