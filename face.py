class Face:
    neutral = 0
    lose = -1
    wow = 1
    win = 2

    def __init__(self):
        self.state = self.neutral
        self.pressed = False
