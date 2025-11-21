from typing import List

class controlflowObfuscation:
    """ Layout-compatible control flow obfuscator.
        Allows main.py to call:

            cfo = controlflowObfuscation()
            code = cfo.run(code)
    """

    def __init__(self):
        pass

    def run(self, code: str) -> str:
        """Main entry point called by GUI"""
        code = self.remove_comments(code)
        code = self.insert_opaque_true_helper(code)
        code = self.insert_opaque_true_in_if(code)
        code = self.shuffle_code_blocks(code)
        code = self.minify_code(code)
        return code


    #  Comment removal
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
                while i < n and code[i] not in "\n\r":
                    i += 1
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

            result_chars.append(c)
            i += 1

        return "".join(result_chars)



    #  Insert opaqueTrue helper
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


    #  Insert opaque predicate into `if` 
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

                    result.append("if")
                    i += 2

                    while i < n and code[i].isspace():
                        result.append(code[i])
                        i += 1

                    # Expect "("
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
                    result.append(c)
                    i += 1
                    continue

            result.append(c)
            i += 1

        return "".join(result)



    #  Shuffle blocks
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
            while i < n and body[i].isspace():
                i += 1
            if i >= n:
                break

            start = i
            brace_depth = 0
            first_brace = -1

            while i < n:
                c = body[i]
                if c == "{":
                    brace_depth += 1
                    if first_brace == -1:
                        first_brace = i
                elif c == "}":
                    brace_depth -= 1
                    if brace_depth == 0 and first_brace != -1:
                        i += 1
                        break
                elif c == ";" and brace_depth == 0 and first_brace == -1:
                    i += 1
                    break
                i += 1

            block = body[start:i]
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

        return header + contract_header + "".join(blocks) + "}" + tail


    #  Minification
    @staticmethod
    def minify_code(code: str) -> str:
        code = "".join(line.strip() for line in code.splitlines())

        result_chars: List[str] = []
        prev = ""
        space_pending = False

        separators = set("{}();,=:+-*/<>!&|[]")

        for ch in code:
            if ch.isspace():
                space_pending = True
                continue

            if space_pending:
                if prev and prev not in separators and ch not in separators:
                    result_chars.append(" ")
                    prev = " "
                space_pending = False

            result_chars.append(ch)
            prev = ch

        return "".join(result_chars).strip()
