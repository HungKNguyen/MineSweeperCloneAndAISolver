from ui import UI
from board import Board
import sys

# Beginner 9-9-10, Intermediate 16-16-40, Expert 16-30-99
if __name__ == "__main__":
    board_size = 16, 16
    bombs = 40
    if len(sys.argv) == 4:
        try:
            board_size = int(sys.argv[1]), int(sys.argv[2])
            bombs = int(sys.argv[3])
        except:
            print("Invalid input, default to Intermediate")
    elif len(sys.argv) == 2:
        if sys.argv[1] == "beginner":
            board_size = 9, 9
            bombs = 10
        elif sys.argv[1] == "intermediate":
            board_size = 16, 16
            bombs = 40
        elif sys.argv[1] == "expert":
            board_size = 16, 30
            bombs = 99
        else:
            print("Invalid input, default to Intermediate")
    piece_size = 25, 25
    board = Board(board_size, bombs)
    ui = UI(board, piece_size)
    ui.run()
