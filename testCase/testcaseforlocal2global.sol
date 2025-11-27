// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/*
    This contract is designed ONLY as a testbed for variable-declaration patterns.

    It includes:
    - State vars vs local vars (shadowing)
    - Locals declared with and without initialization
    - Multiple vars in the same line
    - for / while / do-while loop init variables
    - if/else block-scoped vars
    - named return vars
    - memory vs storage locals
    - struct / enum / mapping locals
    - function parameter locals (value + memory + calldata)
    - function pointer locals
    - try/catch with locals
    - unchecked block locals
    - variables in comments (fake vars, should NOT be touched)
*/

contract VariableCases {
    // ===== Global / state variables (for shadowing tests) =====
    uint256 public globalCounter;
    uint256 public globalInitialized = 42;
    string public globalName;
    address private owner;

    enum Status {
        None,
        Active,
        Inactive
    }

    struct User {
        uint256 id;
        string name;
    }

    mapping(address => User) internal users;

    constructor() {
        owner = msg.sender;
        globalName = "init";
    }

    // ===== CASE 1: Simple locals (with/without init, multiple defs, shadowing) =====
    function simpleLocals() public pure returns (uint256 sum) {
        // Declared without init, assign later
        uint256 a;
        a = 1;

        // Declared with init
        uint256 b = 2;

        // Multiple declarations in sequence
        uint256 c = 3;
        uint256 d; // declared, never assigned

        // Unused local
        uint256 unusedVar = 999;

        // Local bool
        bool flag = true;

        // Tuple declaration + init
        (uint256 e, uint256 f) = (4, 5);

        // Shadowing a state variable name
        uint256 globalCounter = 10; // shadows state `globalCounter`

        // silence warnings
        d;
        flag;
        unusedVar;

        sum = a + b + c + e + f + globalCounter;
    }

    // ===== CASE 2: Loop variables (for / while / do-while) =====
    function loopLocals() public pure returns (uint256 total) {
        // for-loop with init var
        for (uint256 i = 0; i < 5; i++) {
            total += i;
        }

        // for-loop with multiple vars in init & increment
        // for (uint256 j = 0, k = 10; j < 3; j++, k--) {
        //     total += j + k;
        // }

        // while loop
        uint256 index = 0;
        while (index < 2) {
            uint256 tmp = index * 2; // loop-body local
            total += tmp;
            index++;
        }

        // do-while loop
        do {
            uint256 localDoWhile = 1; // scoped only inside do-block
            total += localDoWhile;
        } while (false);
    }

    // ===== CASE 3: Conditionals (if/else, ternary) =====
    function conditionalLocals(uint256 x) public pure returns (uint256) {
        uint256 result;

        if (x > 10) {
            uint256 bigger = x + 1;
            result = bigger;
        } else if (x == 10) {
            uint256 equalCase = 10;
            result = equalCase;
        } else {
            uint256 smaller = x - 1;
            result = smaller;
        }

        // Local defined with ternary expression
        uint256 ternary = x > 5 ? x : 5;

        return result + ternary;
    }

    // ===== CASE 4: Memory / storage / structs / arrays / bytes / address =====
    function memoryAndStorage(
        string memory name,            // parameter: memory local
        bytes calldata extraData       // parameter: calldata local
    ) public returns (string memory) {
        // local memory variable
        string memory localName = name;

        // local storage pointer to mapping element
        User storage u = users[msg.sender];
        u.id = 1;
        u.name = localName;

        // local memory struct
        User memory tempUser = User({id: u.id, name: u.name});

        // local array in memory
        // uint256;
        // arr[0] = 1;
        // arr[1] = 2;
        // arr[2] = 3;

        // // local bytes
        // bytes memory data = abi.encode(tempUser.id, arr[0], extraData.length);

        // local address
        address payable payableOwner = payable(owner);

        // silence warnings
        // data;
        payableOwner;

        return tempUser.name;
    }

    // ===== CASE 5: Named return variables =====
    function namedReturns()
        public
        pure
        returns (uint256 r1, uint256 r2)
    {
        // r1 and r2 are implicit local vars
        r1 = 7;
        r2 = 8;
    }

    // ===== CASE 6: Modifier with local var =====
    modifier onlyOwner() {
        address sender = msg.sender; // local
        require(sender == owner, "not owner");
        _;
    }

    function onlyOwnerCall() external onlyOwner {
        uint256 localInOnlyOwnerCall = 123;
        localInOnlyOwnerCall;
    }

    // ===== CASE 7: Function pointer local =====
    function helper(uint256 x) internal pure returns (uint256) {
        uint256 y = x + 1;
        return y;
    }

    function functionPointerCase(uint256 x) public pure returns (uint256) {
        // function type local variable
        function (uint256) internal pure returns (uint256) fn = helper;
        uint256 result = fn(x);
        return result;
    }

    // ===== CASE 8: try/catch with local vars =====
    function mayRevert(uint256 x) public pure returns (uint256) {
        require(x != 0, "x is zero");
        uint256 y = 100 / x;
        return y;
    }

    function tryCatchCase(uint256 x) public returns (uint256) {
        uint256 value;
        try this.mayRevert(x) returns (uint256 y) {
            uint256 successVar = y + 1;
            value = successVar;
        } catch {
            uint256 errorVar = 0;
            value = errorVar;
        }
        return value;
    }

    // ===== CASE 9: unchecked block locals =====
    function uncheckedCase(uint256 x) public pure returns (uint256) {
        uint256 result;
        unchecked {
            uint256 underflowVar = x - 1;
            result = underflowVar;
        }
        return result;
    }

    // ===== CASE 10: Inline assembly (non-Solidity vars inside) =====
    function assemblyCase() public pure returns (uint256) {
        uint256 z;
        assembly {
            let localAsm := 5
            z := localAsm
        }
        return z;
    }

    // ===== CASE 11: Commented-out variables (should NOT be treated as real) =====

    // The following are fake variables inside comments:
    // uint256 commentedOutVar1;
    // int256 commentedOutVar2 = -1;

    /*
        string commentedBlockVar = "not real";
        uint256 anotherFake;
    */

    function commentRelatedCase() public pure returns (uint256) {
        // uint256 inLineCommentVar = 123;  // also commented out, not real

        // Real variable next to comment
        uint256 realVar = 321; // real variable

        return realVar;
    }
}
