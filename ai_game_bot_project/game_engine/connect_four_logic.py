import math
import random

class ConnectFour:
    def __init__(self, cols=7, rows=6):
        self.cols = cols
        self.rows = rows
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.turn = 1
        
    def drop_piece(self, col, piece):
        if not self.is_valid_location(col):
            return -1
        for r in range(self.rows-1, -1, -1):
            if self.board[r][col] == 0:
                self.board[r][col] = piece
                return r
        return -1
        
    def is_valid_location(self, col):
        return self.board[0][col] == 0

    def get_valid_locations(self):
        return [c for c in range(self.cols) if self.is_valid_location(c)]

    def win_check(self, piece):
        # Horizontal
        for c in range(self.cols-3):
            for r in range(self.rows):
                if self.board[r][c] == piece and self.board[r][c+1] == piece and self.board[r][c+2] == piece and self.board[r][c+3] == piece:
                    return True
        # Vertical
        for c in range(self.cols):
            for r in range(self.rows-3):
                if self.board[r][c] == piece and self.board[r+1][c] == piece and self.board[r+2][c] == piece and self.board[r+3][c] == piece:
                    return True
        # Positively sloped diaganols
        for c in range(self.cols-3):
            for r in range(self.rows-3):
                if self.board[r][c] == piece and self.board[r+1][c+1] == piece and self.board[r+2][c+2] == piece and self.board[r+3][c+3] == piece:
                    return True
        # Negatively sloped diaganols
        for c in range(self.cols-3):
            for r in range(3, self.rows):
                if self.board[r][c] == piece and self.board[r-1][c+1] == piece and self.board[r-2][c+2] == piece and self.board[r-3][c+3] == piece:
                    return True
        return False

    def get_state(self):
        return {
            'board': self.board,
            'turn': self.turn,
            'cols': self.cols,
            'rows': self.rows,
            'game_over': False,
            'winner': None
        }

    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = 1 if piece == 2 else 2

        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(0) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(0) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(0) == 1:
            score -= 4

        return score

    def score_position(self, piece):
        score = 0
        # Center column preference
        center_array = [int(i) for i in list(self.board[:][self.cols//2])]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Horizontal
        for r in range(self.rows):
            row_array = [int(i) for i in list(self.board[r])]
            for c in range(self.cols-3):
                window = row_array[c:c+4]
                score += self.evaluate_window(window, piece)

        # Vertical
        for c in range(self.cols):
            col_array = [int(self.board[r][c]) for r in range(self.rows)]
            for r in range(self.rows-3):
                window = col_array[r:r+4]
                score += self.evaluate_window(window, piece)

        # Diagonals
        for r in range(self.rows-3):
            for c in range(self.cols-3):
                window = [self.board[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        for r in range(self.rows-3):
            for c in range(self.cols-3):
                window = [self.board[r+3-i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        return score

    def minimax(self, depth, alpha, beta, maximizingPlayer):
        valid_locations = self.get_valid_locations()
        is_terminal = self.win_check(1) or self.win_check(2) or len(valid_locations) == 0
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.win_check(2):
                    return (None, 100000000000000)
                elif self.win_check(1):
                    return (None, -10000000000000)
                else: # Game is over, no more valid locations
                    return (None, 0)
            else: # Depth is zero
                return (None, self.score_position(2))

        if maximizingPlayer:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                # Create copy of board
                temp_board_copy = [row[:] for row in self.board]
                # Drop piece in copy
                for r in range(self.rows-1, -1, -1):
                    if temp_board_copy[r][col] == 0:
                        temp_board_copy[r][col] = 2
                        break
                # Recurse
                new_score = self.minimax_with_board(temp_board_copy, depth-1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value

        else: # Minimizing player
            value = math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                temp_board_copy = [row[:] for row in self.board]
                for r in range(self.rows-1, -1, -1):
                    if temp_board_copy[r][col] == 0:
                        temp_board_copy[r][col] = 1
                        break
                new_score = self.minimax_with_board(temp_board_copy, depth-1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value

    def minimax_with_board(self, board, depth, alpha, beta, maximizingPlayer):
        # Helper for recursive calls with arbitrary boards
        valid_locations = [c for c in range(self.cols) if board[0][c] == 0]
        
        def check_win(piece, b):
            for c in range(7-3):
                for r in range(6):
                    if b[r][c] == piece and b[r][c+1] == piece and b[r][c+2] == piece and b[r][c+3] == piece: return True
            for c in range(7):
                for r in range(6-3):
                    if b[r][c] == piece and b[r+1][c] == piece and b[r+2][c] == piece and b[r+3][c] == piece: return True
            for c in range(7-3):
                for r in range(6-3):
                    if b[r][c] == piece and b[r+1][c+1] == piece and b[r+2][c+2] == piece and b[r+3][c+3] == piece: return True
            for c in range(7-3):
                for r in range(3, 6):
                    if b[r][c] == piece and b[r-1][c+1] == piece and b[r-2][c+2] == piece and b[r-3][c+3] == piece: return True
            return False

        is_terminal = check_win(1, board) or check_win(2, board) or len(valid_locations) == 0
        if depth == 0 or is_terminal:
            if is_terminal:
                if check_win(2, board): return (None, 100000000000000)
                elif check_win(1, board): return (None, -10000000000000)
                else: return (None, 0)
            else:
                # Score evaluation for helper
                score = 0
                for r in range(6):
                    row_array = board[r]
                    for c in range(7-3):
                        window = row_array[c:c+4]
                        score += self.evaluate_window(window, 2)
                for c in range(7):
                    col_array = [board[r][c] for r in range(6)]
                    for r in range(6-3):
                        window = col_array[r:r+4]
                        score += self.evaluate_window(window, 2)
                return (None, score)

        if maximizingPlayer:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                b_copy = [r[:] for r in board]
                for r in range(5, -1, -1):
                    if b_copy[r][col] == 0:
                        b_copy[r][col] = 2
                        break
                new_score = self.minimax_with_board(b_copy, depth-1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta: break
            return column, value
        else:
            value = math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                b_copy = [r[:] for r in board]
                for r in range(5, -1, -1):
                    if b_copy[r][col] == 0:
                        b_copy[r][col] = 1
                        break
                new_score = self.minimax_with_board(b_copy, depth-1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta: break
            return column, value
