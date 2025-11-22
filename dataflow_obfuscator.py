import random
import re
import ast
from typing import List, Dict, Set, Any
import string

class EnhancedDataflowObfuscator:
    """
    增强版数据流混淆器
    """
    
    def __init__(self):
        self.temp_variable_counter = 0
        self.global_variables = set()
        self.struct_counter = 0
        self.dynamic_arrays = {}
        self.constant_mappings = {}
        
    def generate_temp_name(self):
        """生成临时变量名"""
        self.temp_variable_counter += 1
        return f"temp_{self.temp_variable_counter}"
    
    def generate_struct_name(self):
        """生成结构体名"""
        self.struct_counter += 1
        return f"DataStruct_{self.struct_counter}"
    
    def is_pure_or_view_function(self, code: str, function_start: int) -> bool:
        """
        判断函数是否为pure或view类型
        """
        # 简单的关键字匹配，实际应用中应该使用完整的语法分析
        function_header = code[function_start:function_start + 100]  # 查看函数开头部分
        return "pure" in function_header or "view" in function_header
    
    def extract_local_variables(self, code):
        """
        提取局部变量信息（简化版，实际应该用完整语法分析）
        """
        variables = []
        
        # 匹配局部变量声明模式
        patterns = [
            r'\b(uint|int|bool|address|string|bytes)\s+(\w+)\s*=\s*[^;]+;',
            r'\b(var\s+(\w+)\s*=\s*[^;]+;)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                var_type = match.group(1) if match.group(1) != 'var' else 'var'
                var_name = match.group(2)
                variables.append({
                    'type': var_type,
                    'name': var_name,
                    'full_match': match.group(0),
                    'start': match.start(),
                    'end': match.end()
                })
        
        return variables
    
    def promote_local_to_global(self, code):
        """
        将局部变量提升为全局变量
        """
        lines = code.split('\n')
        result_lines = []
        global_declarations = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # 跳过pure/view函数
            if any(keyword in line for keyword in ['function', 'function(']):
                # 简单的函数边界检测
                func_start = i
                func_lines = [line]
                i += 1
                
                # 收集整个函数
                brace_count = line.count('{') - line.count('}')
                while i < len(lines) and brace_count > 0:
                    func_lines.append(lines[i])
                    brace_count += lines[i].count('{') - lines[i].count('}')
                    i += 1
                
                func_code = '\n'.join(func_lines)
                
                # 如果不是pure/view函数，处理局部变量提升
                if not self.is_pure_or_view_function(func_code, 0):
                    variables = self.extract_local_variables(func_code)
                    modified_func = func_code
                    
                    for var_info in reversed(variables):  # 反向处理避免位置偏移
                        var_name = f"global_{var_info['name']}"
                        global_decl = f"{var_info['type']} private {var_name};"
                        global_declarations.append(global_decl)
                        
                        # 替换函数内的变量声明为赋值
                        old_declaration = var_info['full_match']
                        if var_info['type'] != 'var':
                            new_assignment = f"{var_name} = {old_declaration.split('=')[1].strip()}"
                        else:
                            new_assignment = f"{var_name} = {old_declaration.split('=')[1].strip()}"
                        
                        modified_func = (modified_func[:var_info['start']] + 
                                       new_assignment + 
                                       modified_func[var_info['end']:])
                    
                    result_lines.extend(modified_func.split('\n'))
                else:
                    result_lines.extend(func_lines)
            else:
                result_lines.append(line)
                i += 1
        
        # 在合约开头插入全局变量声明
        if global_declarations:
            contract_start = -1
            for i, line in enumerate(result_lines):
                if 'contract' in line and '{' in line:
                    contract_start = i + 1
                    break
            
            if contract_start != -1:
                result_lines[contract_start:contract_start] = ['    ' + decl for decl in global_declarations]
        
        return '\n'.join(result_lines)
    
    def create_complex_arithmetic(self, value):
        """
        创建复杂的算术表达式
        """
        if value == 0:
            return "(1 - 1)"
        elif value == 1:
            return "(3 * 5 - 14)"
        
        # 多种复杂表达式生成策略
        strategies = [
            # 加减法组合
            lambda v: f"(({v//2} + {v - v//2}) * {random.randint(1, 3)}) / {random.randint(1, 3)}",
            # 位运算
            lambda v: f"(({v} << {random.randint(0, 2)}) >> {random.randint(0, 2)})",
            # 混合运算
            lambda v: f"({v} * {random.randint(2, 5)}) / {random.randint(2, 5)} + {v % random.randint(2, 5)}"
        ]
        
        strategy = random.choice(strategies)
        return strategy(value)
    
    def constants_to_dynamic_arrays(self, code):
        """
        将常量替换为动态数组访问
        """
        # 识别数字常量
        def replace_constant(match):
            value = int(match.group())
            
            # 为每个值创建唯一的数组和索引
            if value not in self.constant_mappings:
                array_name = f"dataArray_{len(self.constant_mappings)}"
                index = random.randint(0, 100)
                self.constant_mappings[value] = (array_name, index)
                self.dynamic_arrays[array_name] = value
            
            array_name, index = self.constant_mappings[value]
            return f"getDynamicValue(\"{array_name}\", {index})"
        
        # 替换数字常量
        code = re.sub(r'\b\d+\b', replace_constant, code)
        
        # 添加动态数组访问函数
        if self.dynamic_arrays:
            dynamic_function = '''
    function getDynamicValue(string memory arrayName, uint index) private pure returns (uint) {
        bytes32 arrayHash = keccak256(abi.encodePacked(arrayName));
        if (arrayHash == keccak256(abi.encodePacked("dataArray_0"))) return %d;
        ''' % list(self.dynamic_arrays.values())[0]
            
            for i, (name, value) in enumerate(self.dynamic_arrays.items()):
                if i > 0:
                    dynamic_function += f'else if (arrayHash == keccak256(abi.encodePacked("{name}"))) return {value};'
            
            dynamic_function += 'return 0;}'
            
            # 找到合约结束位置插入函数
            code = code.replace('}', dynamic_function + '\n}')
        
        return code
    
    def split_boolean_expressions(self, code):
        """
        拆分布尔表达式
        """
        # 替换true/false为复杂表达式
        replacements = {
            'true': '(true || false) && true',
            'false': '(true && false) || false',
            '== true': '!= false',
            '== false': '!= true'
        }
        
        for old, new in replacements.items():
            code = code.replace(old, new)
        
        # 将简单布尔比较转换为复杂表达式
        comparisons = [
            (r'(\w+)\s*==\s*(\w+)', r'(\1 == \2) && (!(\1 != \2))'),
            (r'(\w+)\s*!=\s*(\w+)', r'(\1 != \2) || (!(\1 == \2))'),
            (r'(\w+)\s*>\s*(\w+)', r'(\1 > \2) && (\1 >= \2 + 1)'),
            (r'(\w+)\s*<\s*(\w+)', r'(\1 < \2) && (\1 <= \2 - 1)')
        ]
        
        for pattern, replacement in comparisons:
            code = re.sub(pattern, replacement, code)
        
        return code
    
    def scalar_to_struct(self, code):
        """
        将标量变量封装为结构体
        """
        # 识别状态变量
        state_var_pattern = r'(\b(uint|int|bool|address|string)\d*\s+)(public|private|internal)?\s*(\w+)\s*;'
        matches = list(re.finditer(state_var_pattern, code))
        
        if not matches:
            return code
        
        # 创建结构体
        struct_name = self.generate_struct_name()
        struct_declaration = f"    struct {struct_name} {{\n"
        
        for match in matches:
            var_type = match.group(1).strip()
            var_name = match.group(4)
            struct_declaration += f"        {var_type} {var_name};\n"
        
        struct_declaration += "    }\n"
        struct_declaration += f"    {struct_name} private dataStruct;\n"
        
        # 替换变量访问
        for match in matches:
            var_name = match.group(4)
            code = code.replace(f" {var_name};", f" _deprecated_{var_name};")  # 注释原变量
            code = re.sub(r'\b' + var_name + r'\b', f"dataStruct.{var_name}", code)
        
        # 插入结构体声明
        contract_start = code.find('{')
        if contract_start != -1:
            code = code[:contract_start+1] + '\n' + struct_declaration + code[contract_start+1:]
        
        return code
    
    def obfuscate(self, code):
        """
        应用所有混淆技术
        """
        print("开始数据流混淆...")
        
        # 1. 标量变量转为结构体
        print("将标量变量转为结构体...")
        code = self.scalar_to_struct(code)
        
        # 2. 局部变量提升为全局变量
        print("提升局部变量为全局变量...")
        code = self.promote_local_to_global(code)
        
        # 3. 常量转换为动态数据
        print("将常量转为动态数据...")
        code = self.constants_to_dynamic_arrays(code)
        
        # 4. 拆分布尔表达式
        print("拆分布尔表达式...")
        code = self.split_boolean_expressions(code)
        
        # 5. 常量转换为算术表达式（原有的）
        print("常量转换为算术表达式...")
        code = self.constants_to_arithmetic(code)
        
        print("数据流混淆完成!")
        return code
    
    def constants_to_arithmetic(self, code):
        """
        将常量转换为复杂算术表达式
        """
        def replace_with_arithmetic(match):
            value = int(match.group())
            if abs(value) < 100:  # 只处理较小的数值
                return self.create_complex_arithmetic(value)
            return match.group()
        
        return re.sub(r'\b\d+\b', replace_with_arithmetic, code)
