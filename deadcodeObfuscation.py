from typing import List

class deadcodeConfig:
    insert_deadcode_helper_config: bool
    insert_bogus_blocks_config: bool

    def __init__(self, _insert_deadcode_helper_config, _insert_bogus_blocks_config):
        self.insert_deadcode_helper_config = _insert_deadcode_helper_config
        self.insert_bogus_blocks_config = _insert_bogus_blocks_config

class deadcodeObfuscation:

    def __init__(self, solContent: str):
        self.solContent = solContent


    def run(self, config: deadcodeConfig) -> str:
        code = self.solContent
        if config.insert_deadcode_helper_config:
            code = self._insert_deadcode_helper(code)
        if config.insert_bogus_blocks_config:
            code = self._insert_bogus_blocks_into_functions(code)
        return code

    # helper

    @staticmethod
    def _find_first_contract_index(code: str) -> int:
        return code.find("contract ")

    def _insert_deadcode_helper(self, code: str) -> str:
        """
        Insert the __dcOpaqueFalse() helper into the first contract if missing.

        Helper is pure (no storage, no environment reads), so it is safe inside
        pure/view/regular functions.
        """
        if "__dcOpaqueFalse(" in code:
            return code  # already inserted

        contract_idx = self._find_first_contract_index(code)
        if contract_idx == -1:
            return code  # no contract, do nothing

        brace_open = code.find("{", contract_idx)
        if brace_open == -1:
            return code

        helper = """
    function __dcOpaqueFalse() private pure returns (bool) {
        uint256 a = 123456789;
        uint256 b = a ^ a;      // 0
        uint256 c = a & b;      // 0
        return (c > a);         // always false
    }
"""

        return code[: brace_open + 1] + helper + code[brace_open + 1 :]


    @staticmethod
    def _is_identifier_char(ch: str) -> bool:
        return ch.isalnum() or ch == "_"

    def _find_function_bodies(self, code: str) -> List[int]:

        positions: List[int] = []
        n = len(code)
        i = 0

        while i < n:
            idx = code.find("function", i)
            if idx == -1:
                break

            # check that 'function' is a standalone keyword
            prev = code[idx - 1] if idx > 0 else " "
            nxt = code[idx + len("function")] if idx + len("function") < n else " "
            if self._is_identifier_char(prev) or self._is_identifier_char(nxt):
                i = idx + len("function")
                continue

            # scan forward to find next '{' or ';'
            j = idx + len("function")
            while j < n and code[j] not in "{;":
                j += 1
            if j >= n:
                break

            if code[j] == ";":
                # e.g. interface or abstract function declaration, skip
                i = j + 1
                continue

            if code[j] == "{":
                positions.append(j)
                i = j + 1
                continue

            i = idx + len("function")

        return positions

    def _insert_bogus_blocks_into_functions(self, code: str) -> str:

        brace_positions = self._find_function_bodies(code)

        if not brace_positions:
            return code

        # dead code snippet (indented with 8 spaces for readability)
        injection = (
            "\n        if (__dcOpaqueFalse()) {\n"
            "            uint256 __dc_dummy = 0;\n"
            "            for (uint256 __dc_i = 0; __dc_i < 3; __dc_i++) {\n"
            "                __dc_dummy = __dc_dummy ^ (__dc_i + 1);\n"
            "            }\n"
            "        }\n"
        )

        # Build new code in one pass using original indices + offset
        parts: List[str] = []
        last_idx = 0
        # positions are in original code; process in order
        for brace_open in brace_positions:
            parts.append(code[last_idx : brace_open + 1])
            parts.append(injection)
            last_idx = brace_open + 1

        parts.append(code[last_idx:])
        return "".join(parts)
