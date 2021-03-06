# MineSweeperClone
This is a simple clone of the Microsoft game, Minesweeper. This project was created using the library pygame for Python. The project also integrated a simple AI that will solve the game. Since Minesweeper doesn't guarantee a solved game, the AI might fail due to random change (in my experience, the AI will solve the game reliably for a game with below 20% mine density).
## How to use
Install pygame:
```
% pip3 install pygame
```
Command line: Move to the project directory then run the main.py file.
```
% python3 main.py
```
By default, this will create a game with 16x16 grid and 40 bombs.
You can also run this in an IDE.
## Additional Setting
You can put an additional argument to indicate preset difficulties:
```
% python3 main.py beginner
```
Three options are "beginner"(9x9 grid 10 bombs), "intermediate"(16x16 grid 40 bombs), and "expert"(16x30 grid 99 bombs).
You can also customise your own game:
```
% python3 main.py 16 16 50
```
The command below create a game with 16x16 grid and 50 bombs.
## How to play:
The rule is the same as the official Minesweeper. The first click will never result in a game over. You can left-click on an empty cell to uncover it, right-click to toggle flagging the cell. Click on the face to reset the game with a new board. There is also an AI mechanism which you can activate by typing "solve" and escape key to stop the AI. Typing "test" will print out the AI's view of the game. Typing "hint" will have the AI move one move for the player.
## AI
The rule of the AI is very simple:
* At the beginning of the game, the AI will simply pick a corner at random
* First, the AI will search for two easy cases by considering one cell:
  * The number of the current cell is equals to the surrounding hidden cells and flagged cells, indicating all hidden cells are mines.
  * The number of the current cell is equals to the surrounding flagged cells, indicating all surrounding hidden cells are not mines.
* Second, the AI will consider situations where interactions between two adjacent cells lead to a valid deduction:
  * This is a generalized form of the 1-1 and 1-2 pattern in Minesweeper
  * The approach include dissecting the area surrounding the two cells into three regions: region only neighboring the first cell(1), region only neighboring the second cell(2), and the region that is neighbor to both cells(3).
* If the AI fails to find any move at this point, it will try to brute force search for cells that most likely to be safe and cells that are guaranteed to be bombs.
* However, that will take too long for most cases, so there is a threshold so that the AI simply take a random cell to click when brute force search takes too long.
* Rinse and repeat until either you win, lose, or stop the AI.
## Credit
The game design was taken inspiration from Daniel Chang.
The algorithm approach was taken inspiration from Code Bullet.
