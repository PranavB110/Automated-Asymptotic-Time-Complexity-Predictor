import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_java as tsjava
import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser

# ── Build language objects ────────────────────────────────────────────────────
PY_LANGUAGE   = Language(tspython.language())
JS_LANGUAGE   = Language(tsjavascript.language())
JAVA_LANGUAGE = Language(tsjava.language())
CPP_LANGUAGE  = Language(tscpp.language())

LANGUAGE_MAP = {
    "python":     PY_LANGUAGE,
    "javascript": JS_LANGUAGE,
    "java":       JAVA_LANGUAGE,
    "cpp":        CPP_LANGUAGE,
}

# ── Node type mappings per language ──────────────────────────────────────────
LOOP_NODES = {
    "python":     ["for_statement", "while_statement"],
    "javascript": ["for_statement", "for_in_statement", "for_of_statement", "while_statement", "do_statement"],
    "java":       ["for_statement", "enhanced_for_statement", "while_statement", "do_statement"],
    "cpp":        ["for_statement", "for_range_loop", "while_statement", "do_statement"],
}

IF_NODES = {
    "python":     ["if_statement"],
    "javascript": ["if_statement"],
    "java":       ["if_statement"],
    "cpp":        ["if_statement"],
}

FUNC_NODES = {
    "python":     ["function_definition"],
    "javascript": ["function_declaration", "function", "arrow_function", "method_definition"],
    "java":       ["method_declaration", "constructor_declaration"],
    "cpp":        ["function_definition"],
}

RETURN_NODES = {
    "python":     ["return_statement"],
    "javascript": ["return_statement"],
    "java":       ["return_statement"],
    "cpp":        ["return_statement"],
}

BREAK_NODES = {
    "python":     ["break_statement"],
    "javascript": ["break_statement"],
    "java":       ["break_statement"],
    "cpp":        ["break_statement"],
}

ASSIGN_NODES = {
    "python":     ["assignment"],
    "javascript": ["variable_declarator", "assignment_expression"],
    "java":       ["variable_declarator", "assignment_expression"],
    "cpp":        ["init_declarator", "assignment_expression"],
}

OP_NODES = {
    "python":     ["binary_operator"],
    "javascript": ["binary_expression"],
    "java":       ["binary_expression"],
    "cpp":        ["binary_expression"],
}

# ── Language detector ─────────────────────────────────────────────────────────
def detect_language(code: str) -> str:
    import re
    code_stripped = code.strip()
    # Java signals — check BEFORE C++ regex
    if any(k in code_stripped for k in ["public class", "public static", "System.out", "String[] args", "extends ", "implements "]):
        return "java"
    # C++ explicit signals
    if any(k in code_stripped for k in ["#include", "cout", "cin", "std::", "::", "->", "int main"]):
        return "cpp"
    # C++ style function: type name(type arg) {
    if re.search(r'\b(int|void|float|double|char|bool|long)\s+\w+\s*\(', code_stripped) and '{' in code_stripped:
        return "cpp"
    # JavaScript signals
    if any(k in code_stripped for k in ["function ", "const ", "let ", "var ", "=>", "console.log"]):
        return "javascript"
    # Python default
    return "python"

# ── Helpers ───────────────────────────────────────────────────────────────────
def count_nodes(node, types):
    count = 1 if node.type in types else 0
    for child in node.children:
        count += count_nodes(child, types)
    return count

def get_max_loop_depth(node, lang, depth=0):
    loop_types = LOOP_NODES[lang]
    max_depth = depth
    for child in node.children:
        if child.type in loop_types:
            child_depth = get_max_loop_depth(child, lang, depth + 1)
        else:
            child_depth = get_max_loop_depth(child, lang, depth)
        max_depth = max(max_depth, child_depth)
    return max_depth

def get_func_name(node, lang):
    func_types = FUNC_NODES[lang]
    for child in node.children:
        if child.type in func_types:
            for subchild in child.children:
                if subchild.type == "identifier":
                    return subchild.text.decode()
        result = get_func_name(child, lang)
        if result:
            return result
    return None

def count_recursive_calls(node, func_name, lang):
    if func_name is None:
        return 0
    count = 0
    call_type = "call" if lang == "python" else "call_expression"
    if node.type == call_type:
        if node.children and node.children[0].type == "identifier":
            if node.children[0].text.decode() == func_name:
                count += 1
    for child in node.children:
        count += count_recursive_calls(child, func_name, lang)
    return count

def has_divide_by_2(node):
    if node.type in ("binary_operator", "binary_expression", "augmented_assignment"):
        text = node.text.decode() if node.text else ""
        if any(p in text for p in ["/ 2", "// 2", "/2", ">> 1"]):
            return True
    for child in node.children:
        if has_divide_by_2(child):
            return True
    return False

# ── Main extractor ────────────────────────────────────────────────────────────
def extract_features_multilang(code: str, language: str = "auto"):
    if language == "auto":
        language = detect_language(code)

    if language not in LANGUAGE_MAP:
        return None, language

    parser = Parser(LANGUAGE_MAP[language])
    tree   = parser.parse(bytes(code, "utf8"))
    root   = tree.root_node

    num_loops      = count_nodes(root, LOOP_NODES[language])
    max_loop_depth = get_max_loop_depth(root, language)
    num_ifs        = count_nodes(root, IF_NODES[language])
    num_funcs      = count_nodes(root, FUNC_NODES[language])
    num_returns    = count_nodes(root, RETURN_NODES[language])
    num_breaks     = count_nodes(root, BREAK_NODES[language])
    num_variables  = count_nodes(root, ASSIGN_NODES[language])
    num_operations = count_nodes(root, OP_NODES[language])
    func_name      = get_func_name(root, language)
    num_recursive  = count_recursive_calls(root, func_name, language)
    divide_by_2    = has_divide_by_2(root)

    while_types = {
        "python":     ["while_statement"],
        "javascript": ["while_statement", "do_statement"],
        "java":       ["while_statement", "do_statement"],
        "cpp":        ["while_statement", "do_statement"],
    }
    for_types = {
        "python":     ["for_statement"],
        "javascript": ["for_statement", "for_in_statement", "for_of_statement"],
        "java":       ["for_statement", "enhanced_for_statement"],
        "cpp":        ["for_statement", "for_range_loop"],
    }

    features = {
        "num_loops":           num_loops,
        "num_nested_loops":    1 if max_loop_depth >= 2 else 0,
        "max_loop_depth":      max_loop_depth,
        "num_ifs":             num_ifs,
        "num_function_defs":   num_funcs,
        "num_recursive_calls": num_recursive,
        "num_return_stmts":    num_returns,
        "num_variables":       num_variables,
        "num_operations":      num_operations,
        "num_comparisons":     0,
        "has_while_loop":      1 if count_nodes(root, while_types[language]) > 0 else 0,
        "has_for_loop":        1 if count_nodes(root, for_types[language]) > 0 else 0,
        "has_break":           1 if num_breaks > 0 else 0,
        "has_divide_by_2":     1 if divide_by_2 else 0,
        "lines_of_code":       len([l for l in code.split("\n") if l.strip()]),
    }

    return features, language


if __name__ == "__main__":
    tests = [
        ("Python — Bubble Sort", "auto", """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""),
        ("JavaScript — Linear Search", "auto", """
function linearSearch(arr, target) {
    for (let i = 0; i < arr.length; i++) {
        if (arr[i] === target) return i;
    }
    return -1;
}
"""),
        ("Java — Binary Search", "auto", """
public static int binarySearch(int[] arr, int target) {
    int l = 0, r = arr.length - 1;
    while (l <= r) {
        int m = (l + r) / 2;
        if (arr[m] == target) return m;
        else if (arr[m] < target) l = m + 1;
        else r = m - 1;
    }
    return -1;
}
"""),
        ("C++ — Triple Loop", "auto", """
int tripleLoop(int n) {
    int count = 0;
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            for (int k = 0; k < n; k++)
                count++;
    return count;
}
"""),
    ]

    for name, lang, code in tests:
        result, detected = extract_features_multilang(code, lang)
        print(f"\n{'='*52}")
        print(f"  {name}  [language: {detected}]")
        print(f"{'='*52}")
        if result:
            for k, v in result.items():
                marker = " ◀" if v > 0 else ""
                print(f"  {k:30s} = {v}{marker}")
        else:
            print("  ERROR: Could not extract features")