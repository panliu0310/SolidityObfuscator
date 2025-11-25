// SPDX-License-Identifier: MIT


contract Counter {
    struct DataStruct_1 {
        uint256 count;
    }
    DataStruct_1 private dataStruct;

    uint256 public _deprecated_count;

    // Function to get the current dataStruct.count
    function get() public view returns (uint256) {
        return _deprecated_count;
    }

    // Function to increment dataStruct.count by 1
    function inc() public {
        dataStruct.count += 1;
    }

    // Function to decrement dataStruct.count by 1
    function dec() public {
        // This function will fail if dataStruct.count = 0
        dataStruct.count -= 1;
    }
}