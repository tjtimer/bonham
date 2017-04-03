import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FUNCTION_CALL = "python root.py -p 9092"

IGNORED_DIRS = [
    "node_modules",
]

GLOB_PATTERNS = [
    '**/*.py',
    '**/*.jsx'
]
