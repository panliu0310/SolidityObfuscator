from typing import List
import re

class controlflowConfig:
    instruction_insert_config: bool
    instruction_replace_config: bool
    insert_opaque_predicate_config: bool
    shuffle_code_blocks_config: bool
    
    def __init__(self, _instruction_insert, _instruction_replace, _insert_opaque_predicate, _shuffle_code_blocks):
        self.instruction_insert_config = _instruction_insert
        self.instruction_replace_config = _instruction_replace
        self.insert_opaque_predicate_config = _insert_opaque_predicate
        self.shuffle_code_blocks_config = _shuffle_code_blocks

class controlflowObfuscation:
    """ Pipeline:
        remove_comments -> insert_opaque_true_helper -> insert_opaque_true_in_if
        -> shuffle_code_blocks -> minify_code
    """

    def __init__(self, code: str):
        # store original Solidity source
        self.code = code

    def run(self, config: controlflowConfig) -> str:
        code = self.code
        #code = self.remove_comments(code) # duplicated function in layout obfuscator
        if config.instruction_insert_config:
            code = self.instruction_insert(code)
        if config.instruction_replace_config:
            code = self.instruction_replace(code)
        if config.insert_opaque_predicate_config:
            code = self.insert_opaque_true_helper(code)
            code = self.insert_opaque_true_in_if(code)
        if config.shuffle_code_blocks_config:
            code = self.shuffle_code_blocks(code)
        #code = self.minify_code(code) # moved to layout obfuscator
        return code
        
	#  duplicated function in layout obfuscator
    #  Comment remove
    @staticmethod
    def remove_comments(code: str) -> str:
        result_chars: List[str] = []
        i = 0
        n = len(code)
        while i < n:
            c = code[i]
            nxt = code[i + 1] if i + 1 < n else ""

            # Line comment
            if c == "/" and nxt == "/":
                i += 2
                # Skip until end of line
                while i < n and code[i] not in "\n\r":
                    i += 1
                # The newline itself we keep (as a separator)
                if i < n:
                    result_chars.append(code[i])
                    i += 1
                continue

            # Block comment
            if c == "/" and nxt == "*":
                i += 2
                while i < n - 1:
                    if code[i] == "*" and code[i + 1] == "/":
                        i += 2
                        break
                    i += 1
                continue

            # Otherwise keep char
            result_chars.append(c)
            i += 1

        return "".join(result_chars)
    
    @staticmethod
    def instruction_insert(code: str) -> str:
        # Match variable assignments like: variable = value;
        # - ([\w.]+): Matches variable names (e.g., `variable`, `obj.property`)
        # - \s*=\s*: Matches the equals sign with optional spaces around it
        # - (\b-?\d+\.*\d+\b);: Matches positive or negative integers or decimals
        insertPattern = r'([\w.]+)\s*=\s*(\b-?\d+\.*\d+\b);'
        code = re.sub(insertPattern, r'\1 = \2 ^ 1 ^ 1;', code)
        return code
    
    @staticmethod
    def instruction_replace(code: str) -> str:
		# a exclusive_or b ==> (a and not b) or (b and not a)
        replace_pattern = r'([\w.]+)\s*\^\s*([\w.]+)'
        code = re.sub(replace_pattern, r'(\1 & ~\2) | (\2 & ~\1)', code)
        return code

    #  Opaque true helper insertion
    @staticmethod
    def _find_first_contract_index(code: str) -> int:
        return code.find("contract ")

    def insert_opaque_true_helper(self, code: str) -> str:
        if "function opaqueTrue(" in code:
            return code

        contract_idx = self._find_first_contract_index(code)
        if contract_idx == -1:
            return code

        brace_open = code.find("{", contract_idx)
        if brace_open == -1:
            return code

        helper = """
    function opaqueTrue() private pure returns (bool) {
        uint256 x = 123456789;
        for (uint256 i = 0; i < 7; i++) {
            x = uint256(keccak256(abi.encodePacked(x, i)));
        }
        return ((x % 2 == 0) || (x % 2 == 1));
    }
"""

        return code[: brace_open + 1] + helper + code[brace_open + 1 :]

    #  Insert opaqueTrue into if conditions
    def insert_opaque_true_in_if(self, code: str) -> str:
        result: List[str] = []
        i = 0
        n = len(code)

        while i < n:
            c = code[i]

            # Detect standalone "if" 
            if c == "i" and i + 1 < n and code[i + 1] == "f":
                prev = code[i - 1] if i > 0 else " "
                nxt = code[i + 2] if i + 2 < n else " "
                if not (prev.isalnum() or prev == "_") and not (nxt.isalnum() or nxt == "_"):
                    # We found an if
                    result.append("if")
                    i += 2

                    while i < n and code[i].isspace():
                        result.append(code[i])
                        i += 1

                    # Expecting '('
                    if i < n and code[i] == "(":
                        start_paren = i
                        depth = 0
                        j = i
                        while j < n:
                            if code[j] == "(":
                                depth += 1
                            elif code[j] == ")":
                                depth -= 1
                                if depth == 0:
                                    break
                            j += 1
                        if j >= n:
                            result.append(code[i:])
                            break

                        condition = code[start_paren + 1 : j]
                        new_cond = f"(({condition}) && opaqueTrue())"
                        result.append("(")
                        result.append(new_cond)
                        result.append(")")
                        i = j + 1
                        continue
                    else:
                        continue
                else:
                    result.append(c)
                    i += 1
                    continue
            # default: copy char
            result.append(c)
            i += 1

        return "".join(result)

    #  Shuffle code blocks 
    @staticmethod
    def _find_matching_brace(text: str, open_index: int) -> int:
        assert text[open_index] == "{"
        depth = 0
        n = len(text)
        for i in range(open_index, n):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return i
        raise ValueError("No matching brace found")

    @staticmethod
    def _split_top_level_blocks(body: str) -> List[str]:
        blocks: List[str] = []
        i = 0
        n = len(body)
        while i < n:
            # Skip whitespace
            while i < n and body[i].isspace():
                i += 1
            if i >= n:
                break

            start = i
            brace_depth = 0
            first_brace_pos = -1

            while i < n:
                c = body[i]
                if c == "{":
                    brace_depth += 1
                    if first_brace_pos == -1:
                        first_brace_pos = i
                elif c == "}":
                    brace_depth -= 1
                    if brace_depth == 0 and first_brace_pos != -1:
                        i += 1
                        break
                elif c == ";" and brace_depth == 0 and first_brace_pos == -1:
                    i += 1
                    break
                i += 1

            end = i
            block = body[start:end]
            if block.strip():
                blocks.append(block)

        return blocks

    def shuffle_code_blocks(self, code: str) -> str:
        contract_idx = self._find_first_contract_index(code)
        if contract_idx == -1:
            return code

        header = code[:contract_idx]
        brace_open = code.find("{", contract_idx)
        if brace_open == -1:
            return code

        contract_header = code[contract_idx: brace_open + 1]
        brace_close = self._find_matching_brace(code, brace_open)
        body = code[brace_open + 1 : brace_close]
        tail = code[brace_close + 1 :]

        blocks = self._split_top_level_blocks(body)

        if len(blocks) > 1:
            blocks = blocks[1:] + blocks[:1]

        new_body = "".join(blocks)
        return header + contract_header + new_body + "}" + tail

    #  Minification
    @staticmethod
    def minify_code(code: str) -> str:
        code = "".join(line.strip() for line in code.splitlines())

        result_chars: List[str] = []
        prev_char = ""
        space_pending = False

        separators = set("{}();,=:+-*/<>!&|[]")

        for ch in code:
            if ch.isspace():
                space_pending = True
                continue

            if space_pending:
                if (prev_char and prev_char not in separators) and (ch not in separators):
                    result_chars.append(" ")
                    prev_char = " "
                space_pending = False

            result_chars.append(ch)
            prev_char = ch

        return "".join(result_chars).strip()
