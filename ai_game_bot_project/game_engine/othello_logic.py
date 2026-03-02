class Othello:
    def __init__(self, size=8):
        self.size = size
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        # Initial 4 pieces in center
        mid = size // 2
        self.board[mid-1][mid-1] = 2 # White
        self.board[mid-1][mid] = 1   # Black
        self.board[mid][mid-1] = 1   # Black
        self.board[mid][mid] = 2     # White
        self.turn = 1 # 1: Black, 2: White
        
    def get_valid_moves(self, player):
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.is_valid_move(r, c, player):
                    moves.append((r, c))
        return moves
        
    def is_valid_move(self, r, c, player):
        if self.board[r][c] != 0:
            return False
        
        other = 3 - player
        directions = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == other:
                # Potential line to flip
                curr_r, curr_c = nr + dr, nc + dc
                while 0 <= curr_r < self.size and 0 <= curr_c < self.size:
                    if self.board[curr_r][curr_c] == 0:
                        break
                    if self.board[curr_r][curr_c] == player:
                        return True
                    curr_r += dr
                    curr_c += dc
        return False

    def make_move(self, r, c, player):
        if not self.is_valid_move(r, c, player):
            return False
            
        self.board[r][c] = player
        other = 3 - player
        directions = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        
        for dr, dc in directions:
            path = []
            nr, nc = r + dr, c + dc
            while 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == other:
                path.append((nr, nc))
                nr += dr
                nc += dc
                if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == player:
                    # Flip path
                    for fr, fc in path:
                        self.board[fr][fc] = player
                    break
        return True

    def get_scores(self):
        s1 = sum(row.count(1) for row in self.board)
        s2 = sum(row.count(2) for row in self.board)
        return s1, s2

    def get_state(self):
        s1, s2 = self.get_scores()
        valid = self.get_valid_moves(self.turn)
        
        # Check if game over (no moves for either)
        game_over = False
        if not valid and not self.get_valid_moves(3 - self.turn):
            game_over = True
            
        return {
            'board': self.board,
            'turn': self.turn,
            'scores': {'1': s1, '2': s2},
            'valid_moves': valid,
            'game_over': game_over,
            'winner': 1 if s1 > s2 else (2 if s2 > s1 else 0) if game_over else None
        }

    def ai_move(self):
        moves = self.get_valid_moves(2) # AI is White (2)
        if not moves:
            return None
            
        # Weighted board for simple heuristic
        weights = [
            [100, -20, 10,  5,  5, 10, -20, 100],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [ 10,  -2,  5,  1,  1,  5,  -2,  10],
            [  5,  -2,  1,  0,  0,  1,  -2,   5],
            [  5,  -2,  1,  0,  0,  1,  -2,   5],
            [ 10,  -2,  5,  1,  1,  5,  -2,  10],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [100, -20, 10,  5,  5, 10, -20, 100],
        ]
        
        best_move = moves[0]
        best_score = -100000
        
        for r, c in moves:
            # Simple heuristic: piece count gained + position weight
            score = weights[r][c]
            # More advanced: simulate flip count? 
            # For now, weighted position is very effective in Othello
            if score > best_score:
                best_score = score
                best_move = (r, c)
                
        return best_move
