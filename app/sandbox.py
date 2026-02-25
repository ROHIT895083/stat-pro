import matplotlib.pyplot as plt

FORBIDDEN_PATTERNS = [
    "import os",
    "import sys",
    "subprocess",
    "eval(",
    "exec(",
    "open("
]

def validate_code(code: str):
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in code:
            return False
    return True

def execute_code(code: str, local_vars: dict):
    if not validate_code(code):
        return {"success": False, "error": "Unsafe code detected"}

    try:
        exec(code, {}, local_vars)
        plt.close('all')
        return {"success": True, "locals": local_vars}

    except Exception as e:
        return {"success": False, "error": str(e)}