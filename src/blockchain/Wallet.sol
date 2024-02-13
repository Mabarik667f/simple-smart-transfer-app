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
        bool status;
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
        require(users[targetAddress].exists, "Account not found");
        return users[targetAddress].name;
    }

    function sendTransferTo(address _recipient) public payable {
        require(msg.value > 0, "Not money");
        require(msg.sender != _recipient, "Can't send to yourself");
        transferHistory.push(Transfer(msg.sender, _recipient, msg.value, block.timestamp, false));
    }

    function confirmToTransfer(uint _indx) public payable {
        require(_indx < transferHistory.length, "Index out of range");
        require(transferHistory[_indx].status == false, "Transfer is completed");
        require(transferHistory[_indx].recipient == msg.sender, "You're not a recipient");
        payable(transferHistory[_indx].recipient).transfer(transferHistory[_indx].amount);
        transferHistory[_indx].status = true;
    }

    function getTransferHistory() public view returns (uint) {
        return transferHistory.length;
    }

    function getTransferDetailsByIndex(uint _indx) public view returns (address, address, uint, uint, bool) {
        require(_indx < transferHistory.length, "Index out of range");
        return (transferHistory[_indx].sender, transferHistory[_indx].recipient, transferHistory[_indx].amount,
        transferHistory[_indx].timestamp, transferHistory[_indx].status);
    }
}
