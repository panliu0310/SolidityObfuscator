import re
import random
import string

from helper import generate_random_name


class LayoutObfuscator:
    """
    Layout Obfuscator
    """

    def __init__(self):
        """
        Initialize the obfuscator
        """
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
                if random.random() > 0.9:  # 10% probability to keep empty line
                    processed_lines.append(line)
                continue
            
            # Process whitespace within the line
            processed_line = ''
            i = 0
            while i < len(line):
                if line[i] == '\t' or line[i] == ' ':
                    if i != 0 and i < len(line)-1 and line[i+1] != '\t' and line[i+1] != ' ':
                        processed_line += line[i]
                        i += 1
                        continue              
                    # Randomly decide whether to keep this whitespace character
                    if random.random() > 0.9:  # 1% probability to keep whitespace
                        processed_line += line[i]
                    i += 1
                else:
                    processed_line += line[i]
                    i += 1
            
            processed_lines.append(processed_line)
        
        processed_code = ''
        for processed_line in processed_lines:
            if random.random() > 0.9:
                processed_code += processed_line + '\n'
            else:
                processed_code += processed_line

        return processed_code
    
    def obfuscate_variables(self, code):
        """
        Obfuscate variable names
        :param code: Input code
        :return: Code with obfuscated variable names
        """
        pattern = r'\b(bool|u?int(8|16|32|64|128|256)?|u?fixed(16x4|32x8|64x10|128x18)|address|string|byte(s[0-9]*)?|enum)\s+(([a-zA-Z_][a-zA-Z0-9_]*)\s+)*(?P<var_name>[a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.finditer(pattern, code)

        for match in matches:
            var_name = match.group('var_name')
            if var_name not in self.variable_map:
                self.variable_map[var_name] = generate_random_name()
                code = re.sub(rf'(?P<stay>"[^"]*")|(?<!msg\.)\b{var_name}\b', lambda x: x.group('stay') if x.group('stay') else self.variable_map[var_name], code)

        return code

    def obfuscate_mappings(self, code):
        '''
        Obfuscate mapping names
        :param code: Input code
        :return: Code with obfuscated mapping names'''
        pattern = r'\bmapping\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=>\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)\s+(([a-zA-Z_][a-zA-Z0-9_]*)\s+)*(?P<mapping_name>[a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.finditer(pattern, code)

        for match in matches:
            mapping_name = match.group('mapping_name')
            if mapping_name not in self.function_map:
                self.function_map[mapping_name] = generate_random_name()
                code = re.sub(rf'(?P<stay>"[^"]*")|\b{mapping_name}\b', lambda x: x.group('stay') if x.group('stay') else self.function_map[mapping_name], code)

        return code
    
    def obfuscate_functions(self, code):
        """
        Obfuscate names of functions, modifiers, contracts, structs, and events
        :param code: Input code
        :return: Code with obfuscated function names
        """
        
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

    def obfuscate(self, code):
        """
        Apply layout obfuscation
        :param code: Input code
        :return: Obfuscated code
        """
        
        # Remove comments
        code = self.remove_comments(code)
        # Obfuscate variable names
        code = self.obfuscate_variables(code)
        # Obfuscate mapping names
        code = self.obfuscate_mappings(code)
        # Obfuscate function names
        code = self.obfuscate_functions(code)
        # Randomly remove whitespace
        code = self.random_remove_whitespace(code)

        return code