#!/usr/bin/python
# -*- coding: utf-8 -*-

import json


class noTouchPure:
    """
    改进版的noTouchPure类，专门用于local2global转换的变量过滤
    过滤掉在pure/view函数中的变量，防止破坏函数的状态可变性
    """

    def __init__(self, _jsonContent):
        self.json = _jsonContent
        self.PURE_FLAG = "pure"
        self.VIEW_FLAG = "view"
        self.CONSTANT_FLAG = "constant"
        self.IMMUTABLE_FLAG = "immutable"

    def findASTNode(self, _key, _value):
        """
        BFS遍历AST查找特定类型的节点
        """
        queue = [self.json]
        result = []

        while queue:
            data = queue.pop()
            for key in data:
                if key == _key and data[key] == _value:
                    result.append(data)
                elif isinstance(data[key], dict):
                    queue.append(data[key])
                elif isinstance(data[key], list):
                    for item in data[key]:
                        if isinstance(item, dict):
                            queue.append(item)
        return result

    def srcToPos(self, _str):
        """
        将src字符串转换为起始和结束位置
        """
        _list = _str.split(":")
        return [int(_list[0]), int(_list[0]) + int(_list[1])]

    def getStartEndPos(self, _list):
        """
        获取节点列表的起始和结束位置
        """
        posList = []
        for item in _list:
            posList.append(self.srcToPos(item["src"]))
        return posList

    def isInRange(self, _list, _sPos, _ePos):
        """
        检查给定的位置范围是否在列表中的任何范围内
        """
        for item in _list:
            if int(_sPos) >= int(item[0]) and int(_ePos) <= int(item[1]):
                return True
        return False

    def findParentFunction(self, variable_node):
        """
        查找变量的父函数
        """
        target_id = variable_node.get("id")
        if not target_id:
            return None

        queue = [self.json]
        function_stack = []

        while queue:
            node = queue.pop()

            if isinstance(node, dict):
                # 如果是函数定义，记录当前函数
                if node.get("name") == "FunctionDefinition":
                    function_stack.append(node)

                # 检查是否找到目标变量
                if node.get("id") == target_id:
                    return function_stack[-1] if function_stack else None

                # 遍历子节点
                for key, value in node.items():
                    if isinstance(value, dict):
                        queue.append(value)
                    elif isinstance(value, list):
                        # 在进入列表前保存函数栈状态
                        current_function_stack = function_stack.copy()
                        for item in value:
                            if isinstance(item, dict):
                                queue.append(item)
                        # 恢复函数栈状态（列表遍历完成）
                        function_stack = current_function_stack

                # 如果是函数定义结束，弹出栈
                if node.get("name") == "FunctionDefinition" and function_stack:
                    function_stack.pop()

        return None

    def isConstantOrImmutable(self, variable_node):
        """
        检查变量是否为常量或不可变变量
        """
        try:
            attributes = variable_node.get("attributes", {})
            return (attributes.get(self.CONSTANT_FLAG) == True or
                    attributes.get(self.IMMUTABLE_FLAG) == True)
        except:
            return False

    def hasSpecialStorageLocation(self, variable_node):
        """
        检查变量是否有特殊的存储位置
        """
        try:
            attributes = variable_node.get("attributes", {})
            storage_location = attributes.get("storageLocation", "default")
            # storage 和 calldata 位置的变量通常不应转换为状态变量
            return storage_location in ["storage", "calldata"]
        except:
            return False

    def isInAssemblyBlock(self, variable_node):
        """
        检查变量是否在assembly块中（简化实现）
        """
        assembly_blocks = self.findASTNode("name", "InlineAssembly")
        if not assembly_blocks:
            return False

        assembly_positions = self.getStartEndPos(assembly_blocks)
        var_sPos, var_ePos = self.srcToPos(variable_node["src"])

        return self.isInRange(assembly_positions, var_sPos, var_ePos)

    def runLocalVar(self, _list):
        """
        主要的过滤方法 - 过滤掉不应被转换为状态变量的局部变量
        """
        # 1. 找到所有pure和view函数节点
        funcNode = self.findASTNode("name", "FunctionDefinition")
        pureViewFuncNode = []

        for func in funcNode:
            state_mutability = func["attributes"].get("stateMutability")
            if state_mutability in [self.PURE_FLAG, self.VIEW_FLAG]:
                pureViewFuncNode.append(func)

        # 2. 获取pure/view函数的起始和中止位置
        posList = self.getStartEndPos(pureViewFuncNode)

        noTouchData = []

        # 3. 过滤变量
        for var in _list:
            # 检查变量是否在pure/view函数中
            sPos, ePos = self.srcToPos(var["src"])
            if self.isInRange(posList, sPos, ePos):
                continue

            # 检查是否为常量或不可变变量
            if self.isConstantOrImmutable(var):
                continue

            # 检查是否有特殊存储位置
            if self.hasSpecialStorageLocation(var):
                continue

            # 检查是否在assembly块中
            if self.isInAssemblyBlock(var):
                continue

            # 检查父函数的其他属性
            parent_function = self.findParentFunction(var)
            if parent_function:
                # 额外的安全检查
                if self._hasOtherRestrictions(parent_function, var):
                    continue

            noTouchData.append(var)

        return noTouchData

    def _hasOtherRestrictions(self, parent_function, variable_node):
        """
        检查其他限制条件
        """
        try:
            # 这里可以添加其他限制条件
            # 例如：检查函数修饰器、特定模式等

            # 示例：检查函数是否有特定的修饰器
            modifiers = parent_function.get("children", [])
            for mod in modifiers:
                if (isinstance(mod, dict) and
                        mod.get("name") == "ModifierInvocation"):
                    # 如果有特定修饰器，可以在这里处理
                    pass

            return False
        except:
            return False

    def getFilteredVariables(self, variable_list, filter_type="all"):
        """
        增强的过滤方法，支持不同类型的过滤
        """
        if filter_type == "pure_view_only":
            # 只过滤pure/view函数中的变量
            return self._filterPureViewOnly(variable_list)
        elif filter_type == "strict":
            # 严格模式，应用所有过滤规则
            return self.runLocalVar(variable_list)
        else:
            # 默认模式
            return self.runLocalVar(variable_list)

    def _filterPureViewOnly(self, variable_list):
        """
        只过滤pure/view函数中的变量
        """
        funcNode = self.findASTNode("name", "FunctionDefinition")
        pureViewFuncNode = []

        for func in funcNode:
            state_mutability = func["attributes"].get("stateMutability")
            if state_mutability in [self.PURE_FLAG, self.VIEW_FLAG]:
                pureViewFuncNode.append(func)

        posList = self.getStartEndPos(pureViewFuncNode)
        filtered_vars = []

        for var in variable_list:
            sPos, ePos = self.srcToPos(var["src"])
            if not self.isInRange(posList, sPos, ePos):
                filtered_vars.append(var)

        return filtered_vars