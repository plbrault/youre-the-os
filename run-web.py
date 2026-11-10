import subprocess
import sys
import tomllib
from pathlib import Path

RUN = 'RUN'
BUILD = 'BUILD'
ARCHIVE = 'ARCHIVE'

mode = 'run'

if len(sys.argv) > 1:
    if sys.argv[1] == 'build':
        mode = BUILD
    elif sys.argv[1] == 'archive':
        mode = ARCHIVE


def cdn_url() -> str:
    pipfile = Path(__file__).parent / 'Pipfile'
    with open(pipfile, 'rb') as file:
        packages = tomllib.load(file)['dev-packages']

    pin = packages['pygbag']

    if not pin.startswith('=='):
        sys.exit(f"Cannot derive the pygbag CDN path from a non-exact pin: {pin}")

    return f"https://plbrault.github.io/youre-the-os-pygbag-cdn/{pin.removeprefix('==')}/"


command = [
    'pygbag',
    '--app_name', 'youre_the_os',
    '--ume_block', '0',
    '--title', "You're the OS!",
    '--template', 'pygbag-template/default.tmpl',
    '--cdn', cdn_url(),
]

if mode == BUILD:
    command.append('--build')
elif mode == ARCHIVE:
    command.append('--archive')

command.append('src')

subprocess.run(command, check=True)
