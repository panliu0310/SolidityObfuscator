import re
import random
import string
from typing import List

def generate_random_name(length=0):
    if length == 0:
        length = random.randrange(8, 16)
    return random.choice(string.ascii_lowercase) + ''.join(random.choices(string.ascii_letters + string.digits, k=length-1))

class layoutConfig:
    remove_comments_config: bool
    obfuscate_variables_config: bool
    obfuscate_mappings_config: bool
    obfuscate_vectors_config: bool
    obfuscate_functions_config: bool
    minify_code_config: bool
    
    def __init__(self, _remove_comments, _obfuscate_variables, _obfuscate_mappings, _obfuscate_vectors, _obfuscate_functions, _minify_code):
        self.remove_comments_config = _remove_comments
        self.obfuscate_variables_config = _obfuscate_variables
        self.obfuscate_mappings_config = _obfuscate_mappings
        self.obfuscate_vectors_config = _obfuscate_vectors
        self.obfuscate_functions_config = _obfuscate_functions
        self.minify_code_config = _minify_code

class layoutObfuscation:
    """Layout Obfuscator"""

    def __init__(self, code):
        """
        Initialize the obfuscator
        """
        self.code = code
        self.variable_map = {}
        self.function_map = {}
    
    def remove_comments(self, source_code):
        """Remove all comments from Solidity code"""
        
        string_pattern = r'(".*?"|\'.*?\')'
        strings = []
        
        def replace_string(match):
            strings.append(match.group(0))
            return f'__STRING_{len(strings)-1}__'

        source_code = re.sub(string_pattern, replace_string, source_code)

        # Remove multi-line comments /* ... */
        source_code = re.sub(r'/\*.*?\*/', '', source_code, flags=re.DOTALL)
        # Remove single-line comments //
        source_code = re.sub(r'//.*', '', source_code)

        for i, string in enumerate(strings):
            source_code = source_code.replace(f'__STRING_{i}__', string)

        return source_code
    
    def random_remove_whitespace(self, source_code):
        """Randomly remove spaces, tabs and empty lines"""
        lines = source_code.split('\n')
        processed_lines = []
        
        for line in lines:
            # Randomly decide whether to delete this line (if it's empty)
            if line.strip() == '':
                if random.random() > 0.95:  # 10% probability to keep empty line
                    processed_lines.append(line)
                continue
            
            # Process whitespace within the line
            processed_line = ''
            i = 0
            inital_space = False
            while i < len(line):
                if line[i] == '\t' or line[i] == ' ':
                    if i==0:
                        inital_space = True
                    if not inital_space and i+1 < len(line) and line[i+1] != '\t' and line[i+1] != ' ':
                        processed_line += line[i]
                        i += 1
                        continue              
                    # Randomly decide whether to keep this whitespace character
                    if random.random() > 0.95:  # 1% probability to keep whitespace
                        processed_line += line[i]
                    i += 1
                else:
                    inital_space = False
                    processed_line += line[i]
                    i += 1
            
            processed_lines.append(processed_line)
        
        processed_code = ''
        for processed_line in processed_lines:
            if random.random() > 0.95:
                processed_code += processed_line + '\n'
            else:
                processed_code += processed_line

        return processed_code
    
    def obfuscate_variables(self, code):
        """Obfuscate variable names"""
        pattern = r'\b(bool|u?int(8|16|32|64|128|256)?|u?fixed(16x4|32x8|64x10|128x18)|address|string|byte(s[0-9]*)?|enum)\s+(([a-zA-Z_][a-zA-Z0-9_]*)\s+)*(?P<var_name>[a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.finditer(pattern, code)

        for match in matches:
            var_name = match.group('var_name')
            if var_name not in self.variable_map:
                self.variable_map[var_name] = generate_random_name()
                code = re.sub(rf'(?P<stay>"[^"]*")|(?<!msg\.)\b{var_name}\b', lambda x: x.group('stay') if x.group('stay') else self.variable_map[var_name], code)

        return code

    def obfuscate_mappings(self, code):
        """Obfuscate mapping names, including nested mappings"""
        code = self.obfuscate_single_mappings(code)
        code = self.obfuscate_nested_mappings(code)
        return code
    
    def obfuscate_single_mappings(self, code):
        """Obfuscate mapping names"""
        pattern = r'\bmapping\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=>\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)\s+(([a-zA-Z_][a-zA-Z0-9_]*)\s+)*(?P<mapping_name>[a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.finditer(pattern, code)

        for match in matches:
            mapping_name = match.group('mapping_name')
            if mapping_name not in self.function_map:
                self.function_map[mapping_name] = generate_random_name()
                code = re.sub(rf'(?P<stay>"[^"]*")|\b{mapping_name}\b', lambda x: x.group('stay') if x.group('stay') else self.function_map[mapping_name], code)

        return code
    
    def obfuscate_nested_mappings(self, code):
        pattern = r'\bmapping\s*\(\s*[^=>]+\s*=>\s*(mapping\s*\(\s*[^=>]+\s*=>\s*)*[^)]+\s*\)(\s*\))*\s+(([a-zA-Z_][a-zA-Z0-9_]*)\s+)*(?P<nested_mapping_name>[a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.finditer(pattern, code)

        for match in matches:
            mapping_name = match.group('nested_mapping_name')
            if mapping_name and mapping_name not in self.variable_map:
                self.variable_map[mapping_name] = generate_random_name()
                code = re.sub(
                    rf'(?P<stay>"[^"]*")|\b{mapping_name}\b', lambda x: x.group('stay') if x.group('stay') else self.variable_map[mapping_name], code
                )

        return code

    def obfuscate_vectors(self, code):
        """Obfuscate array names"""
        pattern = r'\b(bool|u?int(8|16|32|64|128|256)?|u?fixed(16x4|32x8|64x10|128x18)?|address|string|byte(s[0-9]*)?|enum)(\s*\[\s*\d*\s*\])*+\s+(([a-zA-Z_][a-zA-Z0-9_]*)\s+)*(?P<vector_name>[a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.finditer(pattern, code)

        for match in matches:
            vector_name = match.group('vector_name')
            if vector_name not in self.variable_map:
                self.variable_map[vector_name] = generate_random_name()
                code = re.sub(rf'(?P<stay>"[^"]*")|\b{vector_name}\b', lambda x: x.group('stay') if x.group('stay') else self.variable_map[vector_name], code)

        return code

    def obfuscate_functions(self, code):
        """Obfuscate names of functions, modifiers, contracts, structs, and events"""
        excluded_functions = {'fallback', 'receive'}

        pattern = r'(function|modifier|contract|event|struct)\s+(?P<func_name>[a-zA-Z0-9_]*)\s*(\(|\{)'
        matches = re.finditer(pattern, code)

        for match in matches:
            func_name = match.group('func_name')
            
            if func_name in excluded_functions:
                continue
            
            if func_name not in self.function_map:
                self.function_map[func_name] = generate_random_name()
                code = re.sub(rf'(?P<stay>"[^"]*")|\b{func_name}\b', lambda x: x.group('stay') if x.group('stay') else self.function_map[func_name], code)

        return code

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
    
    def run(self, config: layoutConfig):
        """
        Apply layout obfuscation
        :param code: Input code
        :return: Obfuscated code
        """
        
        try:
            code = self.code
            if config.remove_comments_config:
                code = self.remove_comments(code)
            # code = self.random_remove_whitespace(code) # duplicate function from minify_code
            if config.obfuscate_variables_config:
                code = self.obfuscate_variables(code)
            if config.obfuscate_mappings_config:
                code = self.obfuscate_mappings(code)
            if config.obfuscate_vectors_config:
                code = self.obfuscate_vectors(code)
            if config.obfuscate_functions_config:
                code = self.obfuscate_functions(code)
            if config.minify_code_config:
                code = self.minify_code(code)
            return code
        except Exception as e:
            print(f"Error during obfuscation: {e}")
            return code
