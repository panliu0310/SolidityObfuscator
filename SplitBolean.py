#!/usr/bin/python
# -*- coding: utf-8 -*-

from random import randint
from random import random
import json

class SplitBooleanVariables:
    def __init__(self, sol_content, ast_json):
        """
        初始化布尔变量分割器

        Args:
            sol_content: Solidity 源代码
            ast_json: AST 抽象语法树 JSON
        """
        self.sol_content = sol_content
        self.ast_json = ast_json
        self.bool_expressions_pool = self._load_bool_expressions()

    def _load_bool_expressions(self):
        """加载布尔表达式语料库"""
        try:
            with open("bool_corpus.json", "r", encoding="utf-8") as f:
                corpus = json.load(f)
                return corpus.get("boolExpressions", [])
        except:
            # 默认布尔表达式池
            return [
                {"text": "msg.sender != address(0)"},
                {"text": "block.timestamp > 0"},
                {"text": "address(this).balance >= 0"},
                {"text": "bytes4(keccak256('test()')) == 0x12345678"},
                {"text": "tx.origin == msg.sender"}
            ]

    def find_boolean_constants(self, probability=0.8):
        """
        在 AST 中查找所有布尔常量

        Args:
            probability: 选择概率阈值

        Returns:
            List of [value, start_pos, end_pos]
        """
        boolean_constants = []

        def traverse_node(node):
            """递归遍历 AST 节点"""
            if isinstance(node, dict):

                # 检查是否为布尔字面量
                if node.get("nodeType") == "Literal" and node.get("typeDescriptions", {}).get("typeString") == "bool":

                    if random() < probability:
                        src_parts = node["src"].split(":")
                        start_pos = int(src_parts[0])
                        end_pos = start_pos + int(src_parts[1])
                        value = node.get("value", "false")
                        boolean_constants.append([value, start_pos, end_pos])

                # 递归遍历子节点
                for key, value in node.items():
                    if isinstance(value, (dict, list)):
                        traverse_node(value)
            elif isinstance(node, list):
                for item in node:
                    traverse_node(item)

        traverse_node(self.ast_json)
        return boolean_constants

    def split_boolean_expression(self, original_value):
        """
        分割布尔表达式

        Args:
            original_value: 原始布尔值 ('true' 或 'false')

        Returns:
            分割后的表达式字符串
        """
        if original_value.lower() == "true":
            # 对于 true，使用 || 运算符
            return self._generate_or_expression()
        else:
            # 对于 false，使用 && 运算符
            return self._generate_and_expression()

    def _generate_or_expression(self):
        """生成 OR 连接的表达式"""
        choice = randint(0, 1)
        if choice == 0 and self.bool_expressions_pool:
            # 使用布尔表达式
            bool_exp = self.bool_expressions_pool[randint(0, len(self.bool_expressions_pool) - 1)]
            return f" || ({bool_exp['text']})"
        else:
            # 使用算术表达式比较
            return self._generate_arithmetic_comparison()

    def _generate_and_expression(self):
        """生成 AND 连接的表达式"""
        choice = randint(0, 1)
        if choice == 0 and self.bool_expressions_pool:
            # 使用布尔表达式
            bool_exp = self.bool_expressions_pool[randint(0, len(self.bool_expressions_pool) - 1)]
            return f" && ({bool_exp['text']})"
        else:
            # 使用算术表达式比较
            return self._generate_arithmetic_comparison()

    def _generate_arithmetic_comparison(self):
        """生成算术比较表达式"""
        operators = ["==", "!=", ">", "<", ">=", "<="]
        operator = operators[randint(0, len(operators) - 1)]

        # 生成两个随机表达式
        exp1 = self._generate_random_expression()
        exp2 = self._generate_random_expression()

        return f" && ({exp1} {operator} {exp2})" if random() > 0.5 else f" || ({exp1} {operator} {exp2})"

    def _generate_random_expression(self):
        """生成随机表达式"""
        expressions = [
            "block.number",
            "block.timestamp",
            "msg.value",
            "address(this).balance",
            "tx.gasprice",
            str(randint(1, 1000)),
            "uint256(keccak256(abi.encode(block.timestamp)))"
        ]
        return expressions[randint(0, len(expressions) - 1)]

    def apply_boolean_splitting(self, probability=0.8):
        """
        应用布尔变量分割

        Args:
            probability: 转换概率

        Returns:
            修改后的 Solidity 代码
        """
        # 1. 查找所有布尔常量
        boolean_constants = self.find_boolean_constants(probability)

        if not boolean_constants:
            return self.sol_content

        # 2. 按照位置排序（从后往前，避免位置偏移）
        boolean_constants.sort(key=lambda x: x[1], reverse=True)

        # 3. 应用分割
        modified_content = self.sol_content
        for value, start_pos, end_pos in boolean_constants:
            original_text = modified_content[start_pos:end_pos]
            suffix = self.split_boolean_expression(value)
            new_expression = original_text + suffix
            modified_content = modified_content[:start_pos] + new_expression + modified_content[end_pos:]

        return modified_content


# 使用示例
if __name__ == "__main__":
    # 读取 Solidity 文件
    with open("contract.sol", "r", encoding="utf-8") as f:
        solidity_code = f.read()

    # 读取 AST 文件（假设已经生成）
    with open("contract_ast.json", "r", encoding="utf-8") as f:
        ast_data = json.load(f)

    # 创建分割器实例
    splitter = SplitBooleanVariables(solidity_code, ast_data)

    # 应用布尔变量分割
    obfuscated_code = splitter.apply_boolean_splitting(probability=0.8)

    # 保存结果
    with open("contract_obfuscated.sol", "w", encoding="utf-8") as f:
        f.write(obfuscated_code)

    print("布尔变量分割完成！结果保存在 contract_obfuscated.sol")