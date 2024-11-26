import os

dirs = [
    'src',
    'src/assistant_core',
    'src/tests',
    'src/utils'
]

for dir in dirs:
    os.makedirs(dir, exist_ok=True)
