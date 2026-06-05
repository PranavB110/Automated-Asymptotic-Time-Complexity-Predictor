import ast
import math

def extract_features(code: str) -> dict:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    features = {
        "num_loops": 0,
        "num_nested_loops": 0,
        "max_loop_depth": 0,
        "num_ifs": 0,
        "num_function_defs": 0,
        "num_recursive_calls": 0,
        "num_return_stmts": 0,
        "num_variables": 0,
        "num_operations": 0,
        "num_comparisons": 0,
        "has_while_loop": 0,
        "has_for_loop": 0,
        "has_break": 0,
        "has_divide_by_2": 0,
        "lines_of_code": len([l for l in code.split("\n") if l.strip()]),
    }

    func_name = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            features["num_function_defs"] += 1

    def get_loop_depth(node, depth=0):
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                features["num_loops"] += 1
                if isinstance(child, ast.While):
                    features["has_while_loop"] = 1
                if isinstance(child, ast.For):
                    features["has_for_loop"] = 1
                child_depth = get_loop_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = get_loop_depth(child, depth)
                max_depth = max(max_depth, child_depth)
        return max_depth

    features["max_loop_depth"] = get_loop_depth(tree)
    features["num_nested_loops"] = 1 if features["max_loop_depth"] >= 2 else 0

    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            features["num_ifs"] += 1
        elif isinstance(node, ast.Return):
            features["num_return_stmts"] += 1
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            features["num_variables"] += 1
        elif isinstance(node, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)):
            features["num_operations"] += 1
        elif isinstance(node, (ast.Eq, ast.Lt, ast.Gt, ast.LtE, ast.GtE)):
            features["num_comparisons"] += 1
        elif isinstance(node, ast.Break):
            features["has_break"] = 1
        elif isinstance(node, ast.Call):
            if func_name and isinstance(node.func, ast.Name):
                if node.func.id == func_name:
                    features["num_recursive_calls"] += 1
        elif isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.FloorDiv):
                if isinstance(node.right, ast.Constant) and node.right.value == 2:
                    features["has_divide_by_2"] = 1

    return features


if __name__ == "__main__":
    test_code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
    features = extract_features(test_code)
    print("Extracted Features:")
    for k, v in features.items():
        print(f"  {k:30s} = {v}")