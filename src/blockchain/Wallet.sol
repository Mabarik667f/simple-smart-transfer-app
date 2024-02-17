// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.0;

contract App {

    struct User {
        string name;
        bytes32 password;
        bool exists;
    }

    struct Transfer {
        address sender;
        address recipient;
        uint amount;
        uint timestamp;
    }

    mapping (address => User) public users;
    Transfer[] public transferHistory;

    fallback() external payable { }
    receive() external payable { }

    function makeHash(string memory value) public pure returns(bytes32) {
        return keccak256(abi.encodePacked(value));
    }

    function register(address _account, string memory _name, string memory _password) public {
        require(!users[_account].exists, "User founded");
        users[_account] = User(_name, makeHash(_password), true);
    }


    function login(address _account, string memory _password) public view {
        require(users[_account].password == makeHash(_password), "Passwords failed");
    }

    function getBalance() public view returns(uint) {
        return msg.sender.balance;
    }

    function getData(address targetAddress) public view returns(string memory) {
        return users[targetAddress].name;
    }

    function sendTransferTo(address payable _recipient) public payable {
        require(msg.value > 0, "Not money");
        require(msg.sender != _recipient, "Can't send to yourself");
        _recipient.transfer(msg.value);
        transferHistory.push(Transfer(msg.sender, _recipient, msg.value, block.timestamp));
    }

    function getAllTransfersBySender() public view returns (address[] memory, uint[] memory, uint[] memory){
        uint count = 0;

        address[] memory recipients = new address[](4);
        uint[] memory amounts = new uint[](4);
        uint[] memory timestamps = new uint[](4);
        require(transferHistory.length > 0, "No transactions");

        for (uint i = transferHistory.length; i > 0 && count < 4; i--) {
            if (transferHistory[i - 1].sender == msg.sender) {
                recipients[count] = transferHistory[i - 1].recipient;
                amounts[count] = transferHistory[i - 1].amount;
                timestamps[count] = transferHistory[i - 1].timestamp;
                count++;
            }
        }

        return (recipients, amounts, timestamps);
    }

    function getTransferHistory() public view returns (uint) {
        return transferHistory.length;
    }

}
