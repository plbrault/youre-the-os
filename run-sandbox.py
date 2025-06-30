import subprocess
import sys

args = sys.argv[1:]

subprocess.run([
    'python',
    'sandbox.py',
    *args
], cwd='src')
