from solcx import compile_source, install_solc
import json

# 安装指定版本的solc
install_solc('0.8.26')


def generate_ast_from_source(solidity_code):
    """从Solidity源代码生成AST"""
    compiled_sol = compile_source(
        solidity_code,
        output_values=['ast'],
        solc_version='0.8.26'
    )

    # 获取第一个合约的AST
    contract_id, contract_interface = compiled_sol.popitem()
    ast = contract_interface['ast']

    return ast


def generate_ast_from_file(file_path):
    """从Solidity文件生成AST"""
    with open(file_path, 'r', encoding='utf-8') as f:
        solidity_code = f.read()

    return generate_ast_from_source(solidity_code)


# 使用示例
if __name__ == "__main__":
    # 从文件生成
    ast = generate_ast_from_file("contract.sol")

    # 保存AST到文件
    with open("contract_ast.json", "w") as f:
        json.dump(ast, f, indent=2)

    print("AST文件已生成: contract_ast.json")
