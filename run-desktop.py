import subprocess
import sys

subprocess.run([
    'python',
    'main.py',
    *sys.argv[1:]
], cwd='src')
