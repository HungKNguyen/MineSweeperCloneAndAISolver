class SolverView:
    def __init__(self, first_click, bombs_unflagged, lost, won, board_view):
        self.first_click = first_click
        self.bombs_unflagged = bombs_unflagged
        self.lost = lost
        self.won = won
        self.board_view = board_view

    def __str__(self):
        return self.first_click_str() + self.state_str() + self.bombs_unflagged_str() + self.view_str()

    def first_click_str(self):
        return "First Click: " + str(self.first_click) + "\n"

    def state_str(self):
        if self.won:
            string = "Won"
        elif self.lost:
            string = "Lost"
        else:
            string = "Neutral"
        return "State: " + string + "\n"

    def bombs_unflagged_str(self):
        return "Bombs Unflagged: " + str(self.bombs_unflagged) + "\n"

    def view_str(self):
        string = "View:"
        for row in self.board_view:
            string += "\n"
            string += str(row)
        return string


class SolverAction:
    def __init__(self, index, flag):
        self.index = index
        self.flag = flag

    def __str__(self):
        return str(self.index) + " " + str(self.flag)

    def __eq__(self, other):
        return (self.index == other.index) and (self.flag == other.flag)

    def __hash__(self):
        return hash((self.index, self.flag))
