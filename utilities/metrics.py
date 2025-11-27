import math
import re

def calculate_cyclomatic_complexity(code: str) -> int:
    # Count control structures
    complexity = len(re.findall(r'\b(if|for|while|require|switch|case)\b', code))
    return complexity

def calculate_halstead_metrics(code: str):
    # Define regex patterns for operators and operands
    operator_pattern = r'(\+|\-|\*|\/|=|>=|<=|==|!=|&&|\|\||!|{|\}|\(|\)|;|,|\.|:|\[|\]|return|if|for|while|require)'
    operand_pattern = r'\b(?:[a-zA-Z_][a-zA-Z0-9_]*|\d+)\b'
    
    operators = re.findall(operator_pattern, code)
    operands = re.findall(operand_pattern, code)
    
    # Count distinct operators and operands
    N1 = len(operators)
    N2 = len(operands)
    
    distinct_operators = set(operators)
    distinct_operands = set(operands)
    
    n1 = len(distinct_operators)
    n2 = len(distinct_operands)
    
    # Calculate Halstead metrics
    n = n1 + n2 # program vocabulary
    N = N1 + N2 # program length
    calculated_program_length = n1 * math.log(n1, 2) + n2 * math.log(n2, 2) if n1 > 0 and n2 > 0 else 0
    V = N * math.log(n, 2) if n > 0 else 0 # Volume
    D = (n1 / 2) * (N2 / n2) if n2 != 0 else 0 # Difficulty
    E = D * V # Effort
    
    return n1, n2, N1, N2, calculated_program_length, V, D, E

def count_lines_and_comments(code: str):
    lines = code.splitlines()
    total_lines = len(lines)
    comment_lines = sum(1 for line in lines if re.match(r'^\s*(//|/\*|\'\'\')', line))
    return total_lines, comment_lines

def calculate_maintainability_index(code: str):
    n1, n2, N1, N2, calculated_program_length, V, D, E = calculate_halstead_metrics(code)
    G = calculate_cyclomatic_complexity(code)
    L, comment_lines = count_lines_and_comments(code)
    
    # Calculate the percentage of comment lines
    C = (comment_lines / L) * 100 if L > 0 else 0
    C_rad = C * (math.pi / 180)  # Convert percentage to radians

    # Calculate Maintainability Index using the given formula
    MI = 171 - 5.2 * math.log(V, math.e) - 0.23 * G - 16.2 * math.log(L, math.e) + 50 * math.sin(math.sqrt(2.4 * C_rad)) if L > 0 and V > 0 else 0

    return MI

def calculate_complexity(code: str):
    CC = calculate_cyclomatic_complexity(code)
    n1, n2, N1, N2, calculated_program_length, V, D, E = calculate_halstead_metrics(code)
    LOC, comment_lines = count_lines_and_comments(code)
    MI = calculate_maintainability_index(code)
    return f"""Cyclomatic Complexity (CC): {CC}
Distinct Operators (n1): {n1}
Distinct Operands (n2): {n2}
Total Operators (N1): {N1}
Total Operands (N2): {N2}
Volume (V): {V}
Difficulty (D): {D}
Effort (E): {E}
Line of code (LOC): {LOC}
Maintainability Index (MI): {MI}\n"""
    
