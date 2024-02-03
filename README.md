# python-minesweeper

A clean, smooth, and aesthetic Minesweeper game implemented in Python using tkinter. This project relies solely on Python's base modules, requiring no additional dependencies beyond a standard Python installation.

Made with the intent of looking nice and being easy to setup & play.

----
### Table of Contents
1. [Introduction](#python-minesweeper)
2. [Features](#features)
3. [Previews](#previews)
    - [Main Menu](#main-menu)
    - [Highscores](#highscores)
    - [In-game](#in-game)
    - [On loss](#on-loss)
    - [Gameplay](#gameplay)
4. [Installation & Usage](#installation--usage)
5. [Todo](#todo)

## Features

- **Multiple Difficulty Levels**: Choose from Beginner, Intermediate, or Expert levels to match your skill.
- **Highscores Tracking**: Records your best times in a file for each difficulty level, allowing you to track your progress and achievements.
- **Chording**: Allows you to quickly reveal adjacent cells when the number of flags around a numbered cell matches its number.
- **Safe First Click**: The first cell clicked will never be a mine, ensuring a fair start to each game.
- **Imageless Aesthetics**: The game runs entirely using one file, no images or requirements.
- **Impossible Move Alerts**: Numbers that do not logically make sense (e.g: having too many flags) are highlighted in red.

## Previews
### Main Menu
![image](https://github.com/dootss/python-minesweeper/assets/126783585/f05479d4-7ee2-454b-971c-d073a983942a)
### Highscores
![image](https://github.com/dootss/python-minesweeper/assets/126783585/7838a74d-69e4-4491-b88b-058c5592ddb1)
### In-game
![image](https://github.com/dootss/python-minesweeper/assets/126783585/98f6a154-faac-4671-b4ed-4ad2b489910d)
### On loss
![image](https://github.com/dootss/python-minesweeper/assets/126783585/8494462b-3839-4a1e-8683-7edf7516d204)
### Gameplay
https://github.com/dootss/python-minesweeper/assets/126783585/e4c8899a-672a-45d3-97fe-8992b6c30dc3

## Installation & Usage
```
git clone https://github.com/dootss/python-minesweeper.git
cd python-minesweeper
python main.py
```

## Todo
- [ ] Customizable mine count (maybe. it'd make leaderboard tracking harder.)
- [ ] Fix larger grid centering
- [ ] More animations
- [ ] Edge rounding (if even practically possible)
- [ ] Customizable color scheme
