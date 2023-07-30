# You're the OS!

This is a game where you are the operating system of a computer.
As such, you have to manage processes, memory and I/O events.
Make sure not to leave processes idling for too long, or the user will get really impatient and reboot you!

![In-game screenshot](readme-assets/in_game_screenshot.png)

## Prerequisites

* Python 3.11
* [pipenv](https://pypi.org/project/pipenv/)
* An empty `.venv` directory at the root of the project

## Usage

**Install dependencies:** `pipenv install`

**Run as a desktop app:**

```bash
pipenv shell
cd src
python main.py
```

**Run in a web browser:**

```bash
pipenv shell
pygbag src
```

Then open `https://localhost:8000` in your browser.

## License

Copyright (c) 2023 Pier-Luc Brault <pier-luc@brault.me>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Asset Licenses

* Emojis used in the game are from [OpenMoji](https://openmoji.org/). They are published under the [Creative Commons Attribution-ShareAlike License 4.0](https://creativecommons.org/licenses/by-sa/4.0/#).
* The image used in the Game Over screen is by [Aleksandar Cvetanović](https://pixabay.com/fr/users/lemonsandtea-10190089/) and is published under the [Pixabay License](https://pixabay.com/service/license/).
* The game icon was created by user [itim2101](https://www.flaticon.com/authors/itim2101) on [Flaticon](https://www.flaticon.com/) and is published under the [Flaticon license](https://www.freepikcompany.com/legal#nav-flaticon-agreement).
* The primary font used in the game is named *VT323*, and was designed by Peter Hull. The secondary font is named *Victor Mono* and was designed by Rune Bjørnerås. Both are published under the [Open Font License](https://scripts.sil.org/cms/scripts/page.php?item_id=OFL_web).
