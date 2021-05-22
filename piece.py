class Piece:
    def __init__(self, has_bomb, location):
        self.has_bomb = has_bomb
        self.clicked = False
        self.flagged = False
        self.neighbors = None
        self.num_bombs_around = None
        self.location = location

    def toggle_flag(self):
        self.flagged = not self.flagged

    def get_num_bomb_around(self):
        self.num_bombs_around = 0
        for piece in self.neighbors:
            if piece.has_bomb:
                self.num_bombs_around += 1


