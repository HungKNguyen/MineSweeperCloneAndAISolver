import pygame
import os
import threading
import time
from face import Face
from solver import solver_func


class UI:
    def __init__(self, board, piece_size):
        self.images = {}
        self.board = board
        # Size is width x height
        self.piece_size = piece_size
        self.board_size = self.piece_size[0] * self.board.size[1], self.piece_size[1] * self.board.size[0]
        self.digit_size = self.piece_size[0] // 16 * 13, self.piece_size[1] // 16 * 23
        self.face_size = self.piece_size[0] // 16 * 24, self.piece_size[1] // 16 * 24
        self.control_height = self.piece_size[0] // 16 * 43
        self.margin = self.piece_size[0] // 16 * 10
        self.screen_size = self.board_size[0], self.board_size[1] + self.control_height
        self.screen = None
        self.load_images()
        self.time_since_last_reset = 0
        self.time_current = 0
        self.cheat_active = False
        self.cheat_window = False
        self.cheat_input = []
        self.solver_actions = []

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
        pygame.display.set_caption("Minesweeper Clone")
        pygame.display.set_icon(self.images["icon"])
        self.screen.fill((184, 184, 184))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cheat_active = False
                    running = False
                    continue
                if event.type == pygame.VIDEORESIZE:
                    ratio = self.board_size[0] // self.board_size[1]
                    new_h = (event.h // self.board.size[0]) * self.board.size[0]
                    new_w = new_h * ratio
                    self.board_size = new_w, new_h
                    self.piece_size = self.board_size[0] // self.board.size[1], \
                                      self.board_size[1] // self.board.size[0]
                    self.digit_size = self.piece_size[0] // 16 * 13, self.piece_size[1] // 16 * 23
                    self.face_size = self.piece_size[0] // 16 * 24, self.piece_size[1] // 16 * 24
                    self.control_height = self.piece_size[0] // 16 * 43
                    self.margin = self.piece_size[0] // 16 * 10
                    self.screen_size = self.board_size[0], \
                                       self.board_size[1] + self.control_height
                    self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
                    self.screen.fill((184, 184, 184))
                    self.load_images()
                    self.draw()
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN:
                    position = pygame.mouse.get_pos()
                    right_click = pygame.mouse.get_pressed()[2]
                    if self.is_at_face(position, right_click):
                        self.handle_face_pressed()
                    else:
                        self.handle_click(position, right_click)
                    continue
                if event.type == pygame.MOUSEBUTTONUP:
                    position = pygame.mouse.get_pos()
                    right_click = pygame.mouse.get_pressed()[2]
                    if self.is_at_face(position, right_click):
                        self.handle_face_release()
                    continue
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.cheat_active = False
                        continue
                    self.handle_key_input(event.unicode)
                    continue
            if not self.cheat_active:
                self.draw()
            pygame.display.flip()
        pygame.quit()

    def draw(self):
        # Draw mine count
        count_loc = (self.margin, self.margin)
        count = self.board.bombs_unflagged
        for index in range(4):
            image = self.get_digit_image(index, count)
            self.screen.blit(image, count_loc)
            count_loc = count_loc[0] + self.digit_size[0], count_loc[1]
        # Draw face
        face_loc = ((self.screen_size[0] - self.face_size[0]) // 2, self.margin)
        image = self.get_face_image()
        self.screen.blit(image, face_loc)
        # Draw timer
        timer_loc = (self.screen_size[0] - self.margin - 4 * self.digit_size[0], self.margin)
        if not (self.board.won or self.board.lost):
            self.time_current = min((pygame.time.get_ticks() - self.time_since_last_reset) // 1000, 9999)
        for index in range(4):
            image = self.get_digit_image(index, self.time_current)
            self.screen.blit(image, timer_loc)
            timer_loc = timer_loc[0] + self.digit_size[0], timer_loc[1]
        # Draw board
        piece_loc = (0, self.control_height)
        for row in range(self.board.size[0]):
            for col in range(self.board.size[1]):
                piece = self.board.get_piece((row, col))
                if not self.board.lost:
                    image = self.get_image(piece)
                else:
                    image = self.get_lost_image(piece)
                self.screen.blit(image, piece_loc)
                piece_loc = piece_loc[0] + self.piece_size[0], piece_loc[1]
            piece_loc = 0, piece_loc[1] + self.piece_size[1]

    def load_images(self):
        for file_name in os.listdir("images"):
            if file_name.endswith(".png"):
                image = pygame.image.load(r"images/" + file_name)
                if file_name.startswith("digit"):
                    image = pygame.transform.scale(image, self.digit_size)
                elif file_name.startswith("face"):
                    image = pygame.transform.scale(image, self.face_size)
                elif not file_name.startswith("icon"):
                    image = pygame.transform.scale(image, self.piece_size)
                self.images[file_name.split(".")[0]] = image

    def get_image(self, piece):
        string = "empty-block"
        if piece.flagged:
            string = "flag"
        elif piece.clicked:
            if piece.has_bomb:
                string = "bomb-at-clicked-block"
            else:
                string = str(piece.num_bombs_around)
        return self.images[string]

    def get_lost_image(self, piece):
        if piece.flagged:
            if piece.has_bomb:
                string = "flag"
            else:
                string = "wrong-flag"
        elif piece.clicked:
            if piece.has_bomb:
                string = "bomb-at-clicked-block"
            else:
                string = str(piece.num_bombs_around)
        else:
            if piece.has_bomb:
                string = "unclicked-bomb"
            else:
                string = "empty-block"
        return self.images[string]

    def get_digit_image(self, index, digits):
        digits = str(digits)
        if index < 4 - len(digits):
            return self.images["digit-none"]
        if digits[index - 4 + len(digits)] == "-":
            return self.images["digit-dash"]
        return self.images[str("digit-" + digits[index - 4 + len(digits)])]

    def get_face_image(self):
        if self.board.face.state == Face.win:
            string = "face-win"
        elif self.board.face.state == Face.lose:
            string = "face-lose"
        elif self.board.face.state == Face.wow:
            string = "face-wow"
        elif self.board.face.pressed:
            string = "face-pressed"
        else:
            string = "face-default"
        return self.images[string]

    def handle_click(self, position, right_click):
        if self.board.lost or self.board.won:
            return
        pos_y = position[1]
        pos_x = position[0]
        if pos_y > self.control_height:
            index = (pos_y - self.control_height) // self.piece_size[1], pos_x // self.piece_size[0]
            piece = self.board.get_piece(index)
            self.board.handle_click(piece, right_click)

    def is_at_face(self, position, right_click):
        if (self.screen_size[0] - self.face_size[0]) // 2 <= position[0] <= (
                self.screen_size[0] + self.face_size[0]) // 2:
            if self.margin <= position[1] <= self.margin + self.face_size[1]:
                if not right_click:
                    return True
        return False

    def handle_face_pressed(self):
        self.board.face.pressed = True

    def handle_face_release(self):
        self.time_since_last_reset = pygame.time.get_ticks()
        self.board.start()

    def handle_key_input(self, key):
        if not self.cheat_window:
            self.cheat_enter_window_thread()
        self.cheat_input.append(key)
        if self.cheat_input == ["s", "o", "l", "v", "e"]:
            self.cheat_active = True
            self.solve_thread()
        if self.cheat_input == ["t", "e", "s", "t"]:
            print(self.board.give_board_view())


    def cheat_thread_func(self):
        self.cheat_window = True
        time.sleep(1.5)
        self.cheat_window = False
        self.cheat_input.clear()

    def cheat_enter_window_thread(self):
        thread = threading.Thread(target=self.cheat_thread_func)
        thread.start()

    def solve_full_step(self):
        while self.cheat_active and not (self.board.lost or self.board.won):
            current_view = self.board.give_board_view()
            actions = solver_func(current_view)
            while len(actions) > 0:
                action = actions.pop()
                piece = self.board.get_piece(action.index)
                self.board.handle_click(piece, action.flag)
                self.draw()
            time.sleep(0.1)
        self.cheat_active = False

    def solve_thread(self):
        thread = threading.Thread(target=self.solve_full_step)
        thread.start()
