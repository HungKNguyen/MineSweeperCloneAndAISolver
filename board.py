from piece import Piece
from face import Face
from random import sample
import time
from threading import Thread
from solver_components import SolverView


class Board:
    def __init__(self, size, bombs):
        self.first_click = True
        self.board = []
        self.mines_loc = []
        self.size = size
        self.bombs = bombs
        self.bombs_unflagged = self.bombs
        self.lost = False
        self.won = False
        self.num_clicked = 0
        self.set_bombs_loc()
        self.set_board()
        self.face = Face()

    def start(self, blacklist=(0, 0)):
        self.first_click = True
        self.bombs_unflagged = self.bombs
        self.lost = False
        self.won = False
        self.num_clicked = 0
        self.set_bombs_loc(blacklist)
        self.set_board()
        self.face = Face()

    def set_bombs_loc(self, blacklist=(0, 0)):
        self.mines_loc.clear()
        scalar_loc = sample(range(self.size[0] * self.size[1]), self.bombs)
        self.mines_loc = [divmod(x, self.size[1]) for x in scalar_loc]
        if blacklist in self.mines_loc:
            self.mines_loc.remove(blacklist)

    def set_board(self):
        self.board.clear()
        for row in range(self.size[0]):
            list_row = []
            for col in range(self.size[1]):
                has_bomb = ((row, col) in self.mines_loc)
                piece = Piece(has_bomb, (row,col))
                list_row.append(piece)
            self.board.append(list_row)
        self.set_all_neighbors()

    def set_all_neighbors(self):
        for row in range(self.size[0]):
            for col in range(self.size[1]):
                piece = self.get_piece((row, col))
                neighbors = self.get_neighbors((row, col))
                piece.neighbors = neighbors
                piece.get_num_bomb_around()

    def get_neighbors(self, index):
        neighbors = []
        upper = max([0, index[0] - 1])
        lower = min([self.size[0] - 1, index[0] + 1])
        left = max([0, index[1] - 1])
        right = min([self.size[1] - 1, index[1] + 1])
        for row in range(upper, lower + 1):
            for col in range(left, right + 1):
                if row == index[0] and col == index[1]:
                    continue
                neighbors.append(self.get_piece((row, col)))
        return neighbors

    # TODO: Update piece in reaction to click
    def handle_click(self, piece, flag):
        if self.lost or self.won:
            return
        # Flag counts as first click, no more immunity
        if self.first_click:
            self.start(blacklist=piece.location)
            self.first_click = False
            new_piece = self.get_piece(piece.location)
            self.handle_click(new_piece, flag)
            return
        if piece.clicked or (not flag and piece.flagged):
            return
        if flag:
            self.bombs_unflagged -= 1 - (2 * piece.flagged)
            piece.toggle_flag()
            return
        piece.clicked = True
        if piece.has_bomb:
            self.lost = True
            self.face.state = Face.lose
            return
        self.num_clicked += 1
        if piece.num_bombs_around == 0:
            for neighbor in piece.neighbors:
                self.handle_click(neighbor, False)
        if self.num_clicked == self.size[0] * self.size[1] - self.bombs:
            self.won = True
            self.face.state = Face.win
            return
        self.wow_thread()

    def get_piece(self, location):
        return self.board[location[0]][location[1]]

    def give_board_view(self):
        view = []
        for row in range(self.size[0]):
            list_row = []
            for col in range(self.size[1]):
                list_row.append(self.give_piece_view((row, col)))
            view.append(list_row)
        return SolverView(self.first_click, self.bombs_unflagged, self.lost, self.won, view)

    def give_piece_view(self, index):
        piece = self.get_piece(index)
        if piece.flagged:
            return "F"
        if not piece.clicked:
            return "H"
        return str(piece.num_bombs_around)

    def wow(self):
        self.face.state = Face.wow
        time.sleep(0.5)
        if self.won:
            new_state = Face.win
        elif self.lost:
            new_state = Face.lose
        else:
            new_state = Face.neutral
        self.face.state = new_state

    def wow_thread(self):
        thread = Thread(target=self.wow)
        thread.start()


