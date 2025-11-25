import math
import re

def calculate_cyclomatic_complexity(code: str) -> int:
    # Count control structures
    complexity = len(re.findall(r'\b(if|for|while|require|switch|case|else)\b', code))
    return complexity

def calculate_halstead_metrics(code: str):
    # Define regex patterns for operators and operands
    operator_pattern = r'(\+|\-|\*|\/|=|>=|<=|==|!=|&&|\|\||!|{|\}|\(|\)|;|,|\.|:|\[|\]|return|if|for|while|require)'
    operand_pattern = r'\b(?:[a-zA-Z_][a-zA-Z0-9_]*|\d+)\b'
    
    operators = re.findall(operator_pattern, code)
    operands = re.findall(operand_pattern, code)
    
    # Count distinct operators and operands
    n1 = len(operators)
    n2 = len(operands)
    
    distinct_operators = set(operators)
    distinct_operands = set(operands)
    
    N1 = len(distinct_operators)
    N2 = len(distinct_operands)
    
    # Calculate Halstead metrics
    L = n1 + n2
    V = N1 + N2 # vocabulary
    calculated_bugs = (n1 - N1 + n2 - N2) / (N1 + N2) if (N1 + N2) != 0 else 0
    difficulty = (N1 / 2) * (n2 / N2) if N2 != 0 else 0
    effort = difficulty * V
    
    # return {
    #     "Distinct Operators (N1)": N1,
    #     "Distinct Operands (N2)": N2,
    #     "Total Operators (n1)": n1,
    #     "Total Operands (n2)": n2,
    #     "Vocabulary (V)": vocabulary,
    #     "Length (L)": L,
    #     "Calculated Bugs (E)": calculated_bugs,
    #     "Difficulty (D)": difficulty,
    #     "Effort (E)": effort
    # }
    return N1, N2, n1, n2, V

def count_lines_and_comments(code: str):
    lines = code.splitlines()
    total_lines = len(lines)
    comment_lines = sum(1 for line in lines if re.match(r'^\s*(//|/\*|\'\'\')', line))
    return total_lines, comment_lines

def calculate_maintainability_index(code: str):
    N1, N2, n1, n2, V = calculate_halstead_metrics(code)
    G = calculate_cyclomatic_complexity(code)
    L, comment_lines = count_lines_and_comments(code)
    
    # Calculate the percentage of comment lines
    C = (comment_lines / L) * 100 if L > 0 else 0
    C_rad = C * (math.pi / 180)  # Convert percentage to radians

    # Calculate Maintainability Index using the given formula
    MI = 171 - 5.2 * math.log(V) - 0.23 * G - 16.2 * math.log(L) if L > 0 and V > 0 else 0

    return MI

def calculate_complexity(code: str):
    CC = calculate_cyclomatic_complexity(code)
    N1, N2, n1, n2, V = calculate_halstead_metrics(code)
    LOC = count_lines_and_comments(code)
    MI = calculate_maintainability_index(code)
    return f"""Cyclomatic Complexity (CC): {CC}
Distinct Operators (N1): {N1}
Distinct Operands (N2): {N2}
Total Operators (n1): {n1}
Total Operands (n2): {n2}
Vocabulary (V): {V}
Line of code (LOC): {LOC}
Maintainability Index (MI): {MI}\n"""
    
