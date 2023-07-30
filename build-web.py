import subprocess
import sys

build_only = False

if len(sys.argv) > 1 and sys.argv[1] != '--build-only':
    build_only = True

command = [
    'pygbag',
    '--app_name', 'youre_the_os',
    '--ume_block', '0',
    '--title', "You're the OS!",
]

if build_only:
    command.append('--build')

command.append('src')

subprocess.run(command)
