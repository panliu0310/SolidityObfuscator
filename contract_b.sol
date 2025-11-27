// SPDX-License-Identifier: MIT


contract Variables {
	address sender = msg.sender;
	uint256 timestamp = block.timestamp;
	uint256 i = 456;

    // State variables are stored on the blockchain.
    string public text = "Hello";
    uint256 public num = 123;

    function doSomething() public view {
        // Local variables are not saved to the blockchain.
                       

        // Here are some global variables
                                            // Current block timestamp
                                    // address of the caller
    }
}
