import random
import numpy as np

class Game2048:
    def __init__(self):
        self.board = np.zeros((4, 4), dtype=int)
        self.score = 0
        self.game_over = False
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty_cells = list(zip(*np.where(self.board == 0)))
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.board[r][c] = 2 if random.random() < 0.9 else 4

    def stack(self):
        new_board = np.zeros((4, 4), dtype=int)
        for i in range(4):
            fill_pos = 0
            for j in range(4):
                if self.board[i][j] != 0:
                    new_board[i][fill_pos] = self.board[i][j]
                    fill_pos += 1
        self.board = new_board

    def combine(self):
        for i in range(4):
            for j in range(3):
                if self.board[i][j] != 0 and self.board[i][j] == self.board[i][j + 1]:
                    self.board[i][j] *= 2
                    self.board[i][j + 1] = 0
                    self.score += self.board[i][j]

    def move(self, direction):
        # 0: UP, 1: RIGHT, 2: DOWN, 3: LEFT
        initial_board = self.board.copy()
        
        # Rotate board to always perform stack/combine as a LEFT move
        if direction == 0: # UP
            self.board = np.rot90(self.board, 1)
        elif direction == 1: # RIGHT
            self.board = np.rot90(self.board, 2)
        elif direction == 2: # DOWN
            self.board = np.rot90(self.board, 3)
        
        self.stack()
        self.combine()
        self.stack()
        
        # Rotate back
        if direction == 0:
            self.board = np.rot90(self.board, -1)
        elif direction == 1:
            self.board = np.rot90(self.board, -2)
        elif direction == 2:
            self.board = np.rot90(self.board, -3)
            
        if not np.array_equal(initial_board, self.board):
            self.add_new_tile()
            self.check_game_over()
            return True
        return False

    def check_game_over(self):
        if 0 in self.board:
            return False
        for i in range(4):
            for j in range(3):
                if self.board[i][j] == self.board[i][j+1] or self.board[j][i] == self.board[j+1][i]:
                    return False
        self.game_over = True
        return True

    def get_state(self):
        return {
            'board': self.board.tolist(),
            'score': self.score,
            'game_over': self.game_over
        }

    # AI Logic
    def get_best_move(self):
        best_score = -1
        best_move = -1
        for direction in range(4):
            sim_game = Game2048()
            sim_game.board = self.board.copy()
            sim_game.score = self.score
            if sim_game.move(direction):
                score = self.evaluate_board(sim_game.board)
                if score > best_score:
                    best_score = score
                    best_move = direction
        return best_move if best_move != -1 else 0

    def evaluate_board(self, board):
        # Heuristic scoring
        empty_cells = len(np.where(board == 0)[0])
        max_tile = np.max(board)
        
        # Monotonicity
        mono_score = 0
        for i in range(4):
            for j in range(3):
                if board[i][j] >= board[i][j+1]: mono_score += 1
                if board[j][i] >= board[j+1][i]: mono_score += 1
                
        # Smoothness
        smooth_score = 0
        for i in range(4):
            for j in range(3):
                if board[i][j] != 0:
                    k = j + 1
                    while k < 4 and board[i][k] == 0: k += 1
                    if k < 4 and board[i][k] != 0:
                        smooth_score -= abs(np.log2(board[i][j]) - np.log2(board[i][k]))
        
        return empty_cells * 100 + max_tile * 10 + mono_score * 50 + smooth_score * 5
