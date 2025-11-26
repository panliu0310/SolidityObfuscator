#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from noTouchPure import noTouchPure
import random
import copy
import re


class LocalToGlobalConverter:
    """
    Algorithm 3: Converting local variables to global variables
    Input: solidity_source_code, local_variables
    Output: solidity_source_code, global_variables
    """

    def __init__(self, solidity_source_code, ast_json):
        """
        Step 1: Initial Smart Contract Source Code
        """
        self.source_code = solidity_source_code
        self.ast = ast_json
        self.corpus = self.load_corpus()
        self.ntp = noTouchPure(self.ast)

    def load_corpus(self):
        """Load variable naming corpus from configuration"""
        with open("Corpus.txt", "r", encoding="utf-8") as f:
            return json.loads(f.read())

    def find_ast_node(self, key, value, probability=1.0):
        """BFS traversal to find AST nodes with specific key-value pair"""
        queue = [self.ast]

        results = []

        while queue:
            node = queue.pop()
            for k, v in node.items():
                if k == key and v == value and random.random() < probability:
                    results.append(node)
                elif isinstance(v, dict):
                    queue.append(v)
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, dict):
                            queue.append(item)
        return results

    def find_local_variables(self, probability=1.0):
        """
        Step 2: Find localVar_Post - Identify all local variables in the contract
        """
        variable_nodes = self.find_ast_node("nodeType", "VariableDeclaration", probability)

        # with open("ast_node.json", "w", encoding="utf-8") as f:
        #     json.dump(variable_nodes[0], f, indent=2, ensure_ascii=False)

        local_vars = []

        for node in variable_nodes:
            try:
                # Check if it's a local variable (not state variable)
                if node["stateVariable"] == False:
                    local_vars.append(node)
            except:
                continue
        return local_vars

    def src_to_position(self, src_str):
        """Convert src string to start and end positions"""
        parts = src_str.split(":")
        start = int(parts[0])
        length = int(parts[1])
        return [start, start + length]

    def process_duplicate_names(self, local_vars):
        """
        Steps 5-6: Process same names and find same name state
        Handle variable name conflicts
        """
        variable_info = []
        name_count = {}

        print(len(local_vars))

        # Collect variable information
        for var in local_vars:
            try:
                name = var["name"]
                if not name:
                    continue

                start_pos, end_pos = self.src_to_position(var["src"])
                var_id = var["id"]
                variable_info.append([name, start_pos, end_pos, var_id])

                # Count name occurrences
                name_count[name] = name_count.get(name, 0) + 1

            except Exception as e:
                continue

        print(len(name_count))
        # Rename duplicate variables
        rename_list = []
        for name, count in name_count.items():
            if count > 1:
                rename_list.extend(self.rename_variables(name, variable_info))

        # Find all references to renamed variables
        final_rename_list = copy.deepcopy(rename_list)
        for item in rename_list:
            final_rename_list.extend(self.find_variable_references(item))

        return final_rename_list

    def rename_variables(self, original_name, variable_list):
        """Rename variables using corpus names"""
        new_names = []

        for var_info in variable_list:
            if var_info[0] == original_name:
                # Get random name from corpus and shuffle it
                new_name = random.choice(self.corpus["variableNaming"])
                shuffled_name = ''.join(random.sample(new_name, len(new_name)))
                new_names.append([shuffled_name, var_info[1], var_info[2], var_info[3]])

        return new_names

    def find_variable_references(self, variable_info):
        """Find all identifier nodes that reference this variable"""
        identifiers = self.find_ast_node("name", "Identifier", 1.0)
        references = []

        for identifier in identifiers:
            if identifier.get["referencedDeclaration"] == variable_info[3]:
                start_pos, end_pos = self.src_to_position(identifier["src"])
                references.append([variable_info[0], start_pos, end_pos, variable_info[3]])

        return references

    def replace_in_source(self, original_content, replacement_list):
        """Replace variable names in source code"""
        if not replacement_list:
            return original_content

        # Collect all positions that need replacement
        positions = []
        for replacement in replacement_list:
            if replacement[1] != 0 and replacement[2] != 0:
                positions.extend([replacement[1], replacement[2]])

        positions.sort()

        result = ""
        current_pos = 0
        pos_index = 0

        while pos_index < len(positions):
            if pos_index % 2 == 0:
                # Add content before replacement
                result += original_content[current_pos:positions[pos_index]]
                current_pos = positions[pos_index]
                pos_index += 1
            else:
                # Add replacement
                replacement_text = self.get_replacement_text(replacement_list,
                                                             positions[pos_index - 1],
                                                             positions[pos_index])
                result += replacement_text
                current_pos = positions[pos_index]
                pos_index += 1

        result += original_content[current_pos:]
        return result

    def get_replacement_text(self, replacement_list, start_pos, end_pos):
        """Get the replacement text for specific position"""
        for item in replacement_list:
            if item[1] == start_pos and item[2] == end_pos:
                return item[0]
        return ""
    

    def find_decl_statement_for_var(self, var):
        var_id = var["id"]
        queue = [self.ast]
        while queue:
            node = queue.pop()
            if isinstance(node, dict):
                if node.get("nodeType") == "VariableDeclarationStatement":
                    for decl in node.get("declarations", []):
                        if decl and decl.get("id") == var_id:
                            return node
                for v in node.values():
                    if isinstance(v, dict) or isinstance(v, list):
                        queue.append(v)
            elif isinstance(node, list):
                for item in node:
                    if isinstance(item, dict) or isinstance(item, list):
                        queue.append(item)
        return None


    def filter_convertible_variables(self, local_vars):
        filtered = []
        self.var_to_stmt = {}

        for var in local_vars:
            if not var.get("name"):
                continue
            if var.get("storageLocation") != "default":
                continue

            stmt = self.find_decl_statement_for_var(var)
            if stmt is None:
                continue

            filtered.append(var)
            self.var_to_stmt[var["id"]] = stmt

        return filtered



    def create_global_declarations(self, variables):
        declarations = ""

        for var in variables:
            stmt = self.var_to_stmt.get(var["id"])
            if stmt is None:
                start_pos, end_pos = self.src_to_position(var["src"])
            else:
                start_pos, end_pos = self.src_to_position(stmt["src"])

            declaration = self.source_code[start_pos:end_pos]
            declarations += "\t" + declaration + ";\n"

        return declarations


    def remove_local_declarations(self, content, variables):
        modified_content = content

        for var in variables:
            stmt = self.var_to_stmt.get(var["id"])
            if stmt is None:
                continue

            start_pos, end_pos = self.src_to_position(stmt["src"])

            spaces = " " * (end_pos - start_pos)
            modified_content = modified_content[:start_pos] + spaces + modified_content[end_pos+1:]

        return modified_content


    def insert_global_declarations(self, content, declarations):
        """Insert global declarations at the beginning of contract"""
        contract_nodes = self.find_ast_node("nodeType", "ContractDefinition", 1.0)
        if not contract_nodes:

            return content

        contract_start, contract_end = self.src_to_position(contract_nodes[0]["src"])

        # Insert declarations after the contract opening brace
        brace_pos = content.find('{', contract_start, contract_end)
        if brace_pos != -1:
            return content[:brace_pos + 1] + "\n" + declarations + content[brace_pos + 1:]

        return content

    def convert_local_to_global(self, conversion_probability=1):
        """
        Main algorithm: Convert local variables to global variables
        """
        # Step 2: Find local variables
        local_vars = self.find_local_variables(conversion_probability)
        print("Local variables:",len(local_vars))
        if not local_vars:
            return self.source_code, []

        print(local_vars)

        # Step 3-4: Process through AST nodes
        processed_vars = self.ntp.runLocalVar(local_vars)

        # Step 5-6: Handle duplicate names
        rename_list = self.process_duplicate_names(processed_vars)

        # Apply renaming
        renamed_content = self.replace_in_source(self.source_code, rename_list)

        # Reset content after renaming
        self.source_code = renamed_content

        # Filter convertible variables
        convertible_vars = self.filter_convertible_variables(processed_vars)

        if not convertible_vars:
            return self.source_code, []

        # Create global declarations
        global_declarations = self.create_global_declarations(convertible_vars)

        print(global_declarations)


        # Remove local declarations
        content_without_locals = self.remove_local_declarations(self.source_code, convertible_vars)

        # Insert global declarations
        final_content = self.insert_global_declarations(content_without_locals, global_declarations)

        return final_content, convertible_vars


# # Usage Example
# def main():
#     # Example usage
#     with open("contract.sol", "r", encoding="utf-8") as f:
#         solidity_code = f.read()
#
#     with open("contract_ast.json", "r",encoding="utf-8") as f:
#         ast_data = json.load(f)
#
#     # Initialize converter
#     converter = LocalToGlobalConverter(solidity_code, ast_data)
#
#     # Convert local variables to global (80% probability)
#     obfuscated_code, global_vars = converter.convert_local_to_global(0.8)
#
#     print("Conversion completed:")
#     print(f"Converted {len(global_vars)} variables to global")
#     # print("Obfuscated code:")
#     # print(obfuscated_code)
#     with open("contract_new.sol", "w", encoding="utf-8") as f:
#         f.write(obfuscated_code)
#
#
# if __name__ == "__main__":
#     main()