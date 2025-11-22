pragma solidity ^0.8.26;// SPDX-License-Identifier: MIT


contract Counter {
    function __dcOpaqueFalse() private pure returns (bool) {
        if (__dcOpaqueFalse()) {
            uint256 __dc_dummy = 0;
            for (uint256 __dc_i = 0; __dc_i < 3; __dc_i++) {
                __dc_dummy = __dc_dummy ^ (__dc_i + 1);
            }
        }

        uint256 a = 123456789;
        uint256 b = a ^ a;      // 0
        uint256 c = a & b;      // 0
        return (c > a);         // always false
    }

    uint256 public count;

    // Function to get the current count
    function get() public view returns (uint256) {
        if (__dcOpaqueFalse()) {
            uint256 __dc_dummy = 0;
            for (uint256 __dc_i = 0; __dc_i < 3; __dc_i++) {
                __dc_dummy = __dc_dummy ^ (__dc_i + 1);
            }
        }

        return count;
    }

    // Function to increment count by 1
    function inc() public {
        if (__dcOpaqueFalse()) {
            uint256 __dc_dummy = 0;
            for (uint256 __dc_i = 0; __dc_i < 3; __dc_i++) {
                __dc_dummy = __dc_dummy ^ (__dc_i + 1);
            }
        }

        count += 1;
    }

    // Function to decrement count by 1
    function dec() public {
        if (__dcOpaqueFalse()) {
            uint256 __dc_dummy = 0;
            for (uint256 __dc_i = 0; __dc_i < 3; __dc_i++) {
                __dc_dummy = __dc_dummy ^ (__dc_i + 1);
            }
        }

        // This function will fail if count = 0
        count -= 1;
    }
}