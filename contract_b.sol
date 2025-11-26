// SPDX-License-Identifier: MIT


contract IfElse {
	uint256 _x) public pure returns (uint256) {
        // if (_x < getDynamicValue("dataArray_0", 62)) {
        //     return getDynamicValue("dataArray_1", 98);
	uint256 x) public pure returns (uint256) {
        if (x < getDynamicValue("dataArray_0", 62)) {
            return getDynamicValue("dataArray_2", 45);

    function foo(                                                                                      
        } else if (x < getDynamicValue("dataArray_3", 88)) {
            return getDynamicValue("dataArray_1", 98);
        } else {
            return getDynamicValue("dataArray_4", 69);
        }
    }

    function ternary(                                                                                              
        // }
        // return getDynamicValue("dataArray_4", 69);

        // shorthand way to write if / else statement
        // the "?" operator is called the ternary operator
        return _x < getDynamicValue("dataArray_0", 62) ? getDynamicValue("dataArray_1", 98) : getDynamicValue("dataArray_4", 69);
    }

        function getDynamicValue(string memory arrayName, uint index) private pure returns (uint) {
            bytes32 arrayHash = keccak256(abi.encodePacked(arrayName));
    if (arrayHash == keccak256(abi.encodePacked("dataArray_0"))) return 10;
    if (arrayHash == keccak256(abi.encodePacked("dataArray_1"))) return 1;
    if (arrayHash == keccak256(abi.encodePacked("dataArray_2"))) return 0;
    if (arrayHash == keccak256(abi.encodePacked("dataArray_3"))) return 20;
    if (arrayHash == keccak256(abi.encodePacked("dataArray_4"))) return 2;
    return 0;
}
}