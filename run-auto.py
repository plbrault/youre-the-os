import subprocess
import sys

args = sys.argv[1:]

subprocess.run([
	'python',
	'auto.py',
	*args
], cwd='src')
