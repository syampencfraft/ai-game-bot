import math

class TicTacToe:
    def __init__(self, starter='X'):
        self.board = ['' for _ in range(9)]
        self.current_winner = None
        if starter == 'O':
            # AI makes first move if it's 'O'
            self.board[4] = 'O' # Common first move in center

    def print_board(self):
        for row in [self.board[i*3:(i+1)*3] for i in range(3)]:
            print('| ' + ' | '.join(row) + ' |')

    @staticmethod
    def print_board_nums():
        number_board = [[str(i) for i in range(j*3, (j+1)*3)] for j in range(3)]
        for row in number_board:
            print('| ' + ' | '.join(row) + ' |')

    def available_moves(self):
        return [i for i, spot in enumerate(self.board) if spot == '']

    def empty_squares(self):
        return '' in self.board

    def num_empty_squares(self):
        return self.board.count('')

    def make_move(self, square, letter):
        if self.board[square] == '':
            self.board[square] = letter
            if self.winner(square, letter):
                self.current_winner = letter
            return True
        return False

    def winner(self, square, letter):
        row_ind = square // 3
        row = self.board[row_ind*3 : (row_ind+1)*3]
        if all([s == letter for s in row]):
            return True
        col_ind = square % 3
        column = [self.board[col_ind+i*3] for i in range(3)]
        if all([s == letter for s in column]):
            return True
        if square % 2 == 0:
            diagonal1 = [self.board[i] for i in [0, 4, 8]]
            if all([s == letter for s in diagonal1]):
                return True
            diagonal2 = [self.board[i] for i in [2, 4, 6]]
            if all([s == letter for s in diagonal2]):
                return True
        return False

    def get_state(self):
        return {
            'board': self.board,
            'winner': self.current_winner,
            'game_over': not self.empty_squares() or self.current_winner is not None
        }

def minimax(state, player, max_player, min_player):
    if state.current_winner == max_player:
        return {'position': None, 'score': 1 * (state.num_empty_squares() + 1)}
    elif state.current_winner == min_player:
        return {'position': None, 'score': -1 * (state.num_empty_squares() + 1)}
    elif not state.empty_squares():
        return {'position': None, 'score': 0}

    if player == max_player:
        best = {'position': None, 'score': -math.inf}
    else:
        best = {'position': None, 'score': math.inf}

    for possible_move in state.available_moves():
        state.make_move(possible_move, player)
        sim_score = minimax(state, min_player if player == max_player else max_player, max_player, min_player)

        # undo move
        state.board[possible_move] = ''
        state.current_winner = None
        sim_score['position'] = possible_move

        if player == max_player:
            if sim_score['score'] > best['score']:
                best = sim_score
        else:
            if sim_score['score'] < best['score']:
                best = sim_score
    return best
