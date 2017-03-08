import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FUNCTION_CALL = "python root.py"

IGNORED_DIRS = [
    "node_modules",
]

GLOB_PATTERNS = [
    '**/*.py',
    '**/*.jsx'
]
