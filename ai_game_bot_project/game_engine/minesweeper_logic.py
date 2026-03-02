import random

class Minesweeper:
    def __init__(self, width=10, height=10, mines=15):
        self.width = width
        self.height = height
        self.mines_count = mines
        self.board = [[0 for _ in range(width)] for _ in range(height)]
        self.mines = set()
        self.revealed = set()
        self.flags = set()
        self.game_over = False
        self.win = False
        self._place_mines()
        self._calculate_values()

    def _place_mines(self):
        while len(self.mines) < self.mines_count:
            r = random.randint(0, self.height - 1)
            c = random.randint(0, self.width - 1)
            self.mines.add((r, c))

    def _calculate_values(self):
        for r, c in self.mines:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width and (nr, nc) not in self.mines:
                        self.board[nr][nc] += 1

    def reveal(self, r, c):
        if (r, c) in self.revealed or (r, c) in self.flags or self.game_over:
            return
        
        if (r, c) in self.mines:
            self.game_over = True
            self.revealed.update(self.mines)
            return

        self.revealed.add((r, c))
        if self.board[r][c] == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width:
                        self.reveal(nr, nc)

        if len(self.revealed) == (self.width * self.height) - self.mines_count:
            self.win = True
            self.game_over = True

    def toggle_flag(self, r, c):
        if (r, c) in self.revealed or self.game_over:
            return
        if (r, c) in self.flags:
            self.flags.remove((r, c))
        else:
            self.flags.add((r, c))

    def get_state(self):
        display_board = []
        for r in range(self.height):
            row = []
            for c in range(self.width):
                if (r, c) in self.revealed:
                    if (r, c) in self.mines:
                        row.append('M')
                    else:
                        row.append(str(self.board[r][c]))
                elif (r, c) in self.flags:
                    row.append('F')
                else:
                    row.append('H') # Hidden
            display_board.append(row)
        
        return {
            'board': display_board,
            'game_over': self.game_over,
            'win': self.win,
            'mines_left': self.mines_count - len(self.flags)
        }

    # Simple Logical AI
    def get_next_ai_move(self):
        # 1. Check for obvious flags
        for r, c in self.revealed:
            val = self.board[r][c]
            if val == 0: continue
            
            neighbors = self._get_neighbors(r, c)
            hidden = [n for n in neighbors if n not in self.revealed]
            flags = [n for n in neighbors if n in self.flags]
            
            if len(hidden) == val:
                for hr, hc in hidden:
                    if (hr, hc) not in self.flags:
                        return {'type': 'flag', 'pos': (hr, hc)}
            
            if len(flags) == val:
                for hr, hc in hidden:
                    if (hr, hc) not in self.flags:
                        return {'type': 'reveal', 'pos': (hr, hc)}
        
        # 2. Random guess from hidden (if no logic found)
        hidden_total = []
        for r in range(self.height):
            for c in range(self.width):
                if (r, c) not in self.revealed and (r, c) not in self.flags:
                    hidden_total.append((r, c))
        
        if hidden_total:
            return {'type': 'reveal', 'pos': random.choice(hidden_total)}
        return None

    def _get_neighbors(self, r, c):
        res = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    res.append((nr, nc))
        return res
