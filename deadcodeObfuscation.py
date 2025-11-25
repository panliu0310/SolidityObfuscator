import re
import random
from typing import List, Optional


class deadcodeConfig:
    insert_deadcode_helper_config: bool
    insert_bogus_blocks_config: bool

    def __init__(self, insert_helper: bool = True, insert_blocks: bool = True):
        self.insert_deadcode_helper_config = insert_helper
        self.insert_bogus_blocks_config = insert_blocks


class deadcodeObfuscation:

    def __init__(self, solContent: str):
        self.solContent = solContent

    def run(self, config: Optional[deadcodeConfig] = None) -> str:
        code = self.solContent

        # default config if none
        if config is None:
            config = deadcodeConfig(True, True)

        if config.insert_deadcode_helper_config:
            code = self._insert_deadcode_helper(code)

        if config.insert_bogus_blocks_config:
            code = self._insert_bogus_blocks_into_functions(code)

        return code


    @staticmethod
    def _find_first_contract_index(code: str) -> int:
        return code.find("contract ")

    def _insert_deadcode_helper(self, code: str) -> str:
        if "function __dcOpaqueFalse()" in code:
            return code

        contract_idx = self._find_first_contract_index(code)
        if contract_idx == -1:
            return code

        brace_open = code.find("{", contract_idx)
        if brace_open == -1:
            return code

        helper = """
    function __dcOpaqueFalse() private pure returns (bool) {
        uint256 x;
        assembly {
            let a := 1
            let b := 1
            x := sub(a, b)
        }
        return (x > 1);
    }
"""

        return code[: brace_open + 1] + helper + code[brace_open + 1 :]

    @staticmethod
    def _function_matches(code: str) -> List[re.Match]:
        """
        Find all function-like definitions with bodies:

          function foo(...) ... { ... }
          constructor() ... { ... }
          fallback() external payable { ... }
          receive() external payable { ... }

        group(2) is the function name if it exists (only for 'function name(...)').
        """
        pattern = re.compile(
            r"""
            \b(
                function\s+([A-Za-z_][A-Za-z0-9_]*) |   
                constructor\s* |                        
                fallback\s*\( |                       
                receive\s*\(                           
            )
            [^{;]*                                    
            \{                                          
            """,
            re.VERBOSE,
        )
        return list(pattern.finditer(code))

    def _insert_bogus_blocks_into_functions(self, code: str) -> str:
        matches = self._function_matches(code)
        if not matches:
            return code

        # Choose a global probability p between 0.4 and 0.6
        p = random.uniform(0.4, 0.6)

        parts: List[str] = []
        last_index = 0

        for m in matches:
            brace_pos = code.find("{", m.start())
            if brace_pos == -1:
                continue

            func_name = m.group(2) if len(m.groups()) >= 2 else None

            if func_name and func_name.startswith("__dcOpaqueFalse"):
                continue

            # randomize
            if random.random() >= p:
                continue


            line_start = code.rfind("\n", 0, brace_pos)
            if line_start == -1:
                line_start = 0
            else:
                line_start += 1

            leading_segment = code[line_start:brace_pos]
            leading_ws_match = re.match(r"[ \t]*", leading_segment)
            base_indent = leading_ws_match.group(0) if leading_ws_match else ""
            body_indent = base_indent + "    "

            variant = random.randint(0, 2)
            injection = self._build_dead_block(body_indent, variant=variant)

            parts.append(code[last_index : brace_pos + 1])
            parts.append(injection)
            last_index = brace_pos + 1

        # Append remaining tail
        parts.append(code[last_index:])
        return "".join(parts)

    @staticmethod
    def _build_dead_block(body_indent: str, variant: int = 0) -> str:
        bi = body_indent
        bi2 = body_indent + "    "
        bi3 = body_indent + "        "

        if variant == 0:
            # Variant A
            return (
                f"\n{bi}if (__dcOpaqueFalse()) {{\n"
                f"{bi2}uint256 __dc_dummy = 0;\n"
                f"{bi2}for (uint256 __dc_i = 0; __dc_i < 5; __dc_i++) {{\n"
                f"{bi3}__dc_dummy ^= (__dc_i * 7 + 3);\n"
                f"{bi3}if ((__dc_dummy & 1) == 0) {{\n"
                f"{bi3}    __dc_dummy = (__dc_dummy >> 1) ^ 0xA5A5;\n"
                f"{bi3}}} else {{\n"
                f"{bi3}    __dc_dummy = (__dc_dummy << 1) ^ 0x5A5A;\n"
                f"{bi3}}}\n"
                f"{bi2}}}\n"
                f"{bi2}require(__dc_dummy != 42, \"dc_a\");\n"
                f"{bi}}}\n"
            )

        if variant == 1:
            # Variant B
            return (
                f"\n{bi}if (__dcOpaqueFalse()) {{\n"
                f"{bi2}uint256 __dc_acc = 1;\n"
                f"{bi2}for (uint256 __dc_i = 0; __dc_i < 3; __dc_i++) {{\n"
                f"{bi3}for (uint256 __dc_j = 0; __dc_j < 2; __dc_j++) {{\n"
                f"{bi3}    __dc_acc = (__dc_acc * 31 + __dc_i + __dc_j);\n"
                f"{bi3}    if ((__dc_acc & 3) == 1) {{\n"
                f"{bi3}        __dc_acc ^= 0xFF;\n"
                f"{bi3}    }} else if ((__dc_acc & 3) == 2) {{\n"
                f"{bi3}        __dc_acc ^= 0xAA;\n"
                f"{bi3}    }} else {{\n"
                f"{bi3}        __dc_acc ^= 0x55;\n"
                f"{bi3}    }}\n"
                f"{bi3}}}\n"
                f"{bi2}}}\n"
                f"{bi2}require(__dc_acc != 0xDEADBEEF, \"dc_b\");\n"
                f"{bi}}}\n"
            )

        # Variant C
        return (
            f"\n{bi}if (__dcOpaqueFalse()) {{\n"
            f"{bi2}uint256 __dc_x = 0;\n"
            f"{bi2}uint256 __dc_y = 1;\n"
            f"{bi2}for (uint256 __dc_k = 0; __dc_k < 4; __dc_k++) {{\n"
            f"{bi3}__dc_x = (__dc_x + __dc_y) ^ (__dc_k * 13);\n"
            f"{bi3}__dc_y = (__dc_y * 5) ^ (__dc_x >> 1);\n"
            f"{bi3}if ((__dc_x & 7) == 3) {{\n"
            f"{bi3}    __dc_y ^= 0x1234;\n"
            f"{bi3}}}\n"
            f"{bi2}}}\n"
            f"{bi2}if (__dc_x == 0xCAFEBABE) {{\n"
            f"{bi3}revert(\"dc_c\");\n"
            f"{bi2}}}\n"
            f"{bi}}}\n"
        )
