import random

class Sudoku:
    def __init__(self, empty_cells=40):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.original = [[False for _ in range(9)] for _ in range(9)]
        self.game_over = False
        self._generate_puzzle(empty_cells)

    def _generate_puzzle(self, empty_cells):
        # 1. Fill diagonal 3x3 blocks
        for i in range(0, 9, 3):
            self._fill_box(i, i)
        
        # 2. Fill remaining
        self._solve_sudoku(self.board)
        
        # 3. Remove digits
        count = empty_cells # Number of empty cells
        while count > 0:
            r, c = random.randint(0, 8), random.randint(0, 8)
            if self.board[r][c] != 0:
                self.board[r][c] = 0
                count -= 1
        
        # Mark original numbers
        for r in range(9):
            for c in range(9):
                if self.board[r][c] != 0:
                    self.original[r][c] = True

    def _fill_box(self, row, col):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for i in range(3):
            for j in range(3):
                self.board[row+i][col+j] = nums.pop()

    def _is_safe(self, board, row, col, num):
        # Check row
        if num in board[row]: return False
        # Check col
        if num in [board[i][col] for i in range(9)]: return False
        # Check 3x3
        sr, sc = (row // 3) * 3, (col // 3) * 3
        for i in range(3):
            for j in range(3):
                if board[sr+i][sc+j] == num: return False
        return True

    def _solve_sudoku(self, board):
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    for num in range(1, 10):
                        if self._is_safe(board, r, c, num):
                            board[r][c] = num
                            if self._solve_sudoku(board):
                                return True
                            board[r][c] = 0
                    return False
        return True

    def make_move(self, r, c, num):
        if self.original[r][c] or self.game_over:
            return False
        if num == 0 or self._is_safe(self.board, r, c, num):
            self.board[r][c] = num
            self.check_win()
            return True
        return False

    def check_win(self):
        # Simple check: no zeros left (assuming moves are safe)
        for r in range(9):
            if 0 in self.board[r]: return False
        self.game_over = True
        return True

    def get_state(self):
        return {
            'board': self.board,
            'original': self.original,
            'game_over': self.game_over
        }

    # AI Solver
    def solve_step(self):
        if self.game_over: return
        # Find first empty
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    # Find correct num (since we know the full solution exists)
                    # For simplicity, we just solve the current board from scratch 
                    # but we need to find the correct number for THAT cell.
                    # We'll just run the solver and pick the first correct number.
                    temp_board = [row[:] for row in self.board]
                    self._solve_sudoku(temp_board)
                    self.board[r][c] = temp_board[r][c]
                    self.check_win()
                    return {'r': r, 'c': c, 'val': self.board[r][c]}
        return None
