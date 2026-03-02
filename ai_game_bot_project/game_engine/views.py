from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Score
import json
from .snake_game import SnakeGame
from .tictactoe_logic import TicTacToe, minimax
from .game2048_logic import Game2048
from .minesweeper_logic import Minesweeper
from .sudoku_logic import Sudoku
from .connect_four_logic import ConnectFour
from .othello_logic import Othello
import random
from .ai_agent import AIAgent
from .q_learning_agent import QLearningAgent
import math

# Global game and agent instances
valid_games = {}
valid_agents = {} # session_id -> agent_instance

def _get_common_context(request):
    top_scores = Score.objects.order_by('-score')[:10]
    user_high_score = 0
    if request.user.is_authenticated:
        user_scores = Score.objects.filter(user=request.user).order_by('-score')
        if user_scores.exists():
            user_high_score = user_scores.first().score
    return {
        'top_scores': top_scores,
        'user_high_score': user_high_score
    }

def index(request):
    """Renders the main landing page."""
    return render(request, 'index.html', _get_common_context(request))

@login_required
def snake_view(request):
    """Renders the Snake game page."""
    return render(request, 'games/snake.html', _get_common_context(request))

@login_required
def tictactoe_view(request):
    """Renders the Tic-Tac-Toe game page."""
    return render(request, 'games/tictactoe.html', _get_common_context(request))

@login_required
def game2048_view(request):
    """Renders the 2048 game page."""
    return render(request, 'games/2048.html', _get_common_context(request))

@login_required
def minesweeper_view(request):
    """Renders the Minesweeper game page."""
    return render(request, 'games/minesweeper.html', _get_common_context(request))

@login_required
def sudoku_view(request):
    """Renders the Sudoku game page."""
    return render(request, 'games/sudoku.html', _get_common_context(request))

@login_required
def connect_four_view(request):
    """Renders the Connect Four game page."""
    return render(request, 'games/connect_four.html', _get_common_context(request))

@login_required
def othello_view(request):
    """Renders the Othello game page."""
    return render(request, 'games/othello.html', _get_common_context(request))

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

@csrf_exempt
def save_score(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            score_val = data.get('score', 0)
            
            # Simple logic: save every game? Or only high scores?
            # Let's save every game for history, leaderboard query does the rest.
            Score.objects.create(user=request.user, score=score_val)
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'ignored'})

@csrf_exempt
def start_game(request):
    """Initializes a new game with selected agent."""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)

    game_type = request.GET.get('game', 'snake')
    mode = request.GET.get('mode', 'astar')
    
    if game_type == 'tictactoe':
        starter = request.GET.get('starter', 'X')
        game = TicTacToe(starter=starter)
        state = game.get_state()
    elif game_type == '2048':
        game = Game2048()
        state = game.get_state()
    elif game_type == 'minesweeper':
        w = int(request.GET.get('w', 10))
        h = int(request.GET.get('h', 10))
        m = int(request.GET.get('m', 15))
        game = Minesweeper(width=w, height=h, mines=m)
        state = game.get_state()
    elif game_type == 'sudoku':
        empty = int(request.GET.get('empty', 40))
        game = Sudoku(empty_cells=empty)
        state = game.get_state()
    elif game_type == 'connect_four':
        game = ConnectFour()
        state = game.get_state()
    elif game_type == 'othello':
        game = Othello()
        state = game.get_state()
    else:
        w = int(request.GET.get('w', 20))
        h = int(request.GET.get('h', 20))
        game = SnakeGame(width=w, height=h)
        state = game.reset()
    
    # Store in global dict
    session_id = request.session.session_key or 'default'
    if not request.session.session_key:
        request.session.create()
        session_id = request.session.session_key
        
    valid_games[session_id] = game
    
    # Select Agent
    if game_type == 'tictactoe':
        if mode == 'manual':
            valid_agents[session_id] = 'manual'
        else:
            valid_agents[session_id] = 'minimax'
    elif game_type == '2048':
        if mode == 'manual':
            valid_agents[session_id] = 'manual'
        else:
            valid_agents[session_id] = 'heuristic'
    elif game_type == 'minesweeper':
        if mode == 'manual':
            valid_agents[session_id] = 'manual'
        else:
            valid_agents[session_id] = 'logical'
    elif game_type == 'sudoku':
        if mode == 'manual':
            valid_agents[session_id] = 'manual'
        else:
            valid_agents[session_id] = 'solver'
    elif game_type == 'connect_four':
        if mode == 'manual':
            valid_agents[session_id] = 'manual'
        else:
            valid_agents[session_id] = 'ai' # AI logic is in game_step
    elif game_type == 'othello':
        if mode == 'manual':
            valid_agents[session_id] = 'manual'
        else:
            valid_agents[session_id] = 'ai' # AI logic is in game_step
    else:
        if mode == 'qlearning':
            if session_id not in valid_agents or not isinstance(valid_agents[session_id], QLearningAgent):
                 valid_agents[session_id] = QLearningAgent(game)
            else:
                 valid_agents[session_id].game = game
        elif mode == 'manual':
            valid_agents[session_id] = 'manual'
        else:
            valid_agents[session_id] = AIAgent(game)
    
    return JsonResponse(state)

@csrf_exempt
def game_step(request):
    """Calculates AI move and steps the game."""
    if not request.user.is_authenticated:
         return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)

    session_id = request.session.session_key or 'default'
    game = valid_games.get(session_id)
    agent = valid_agents.get(session_id)
    
    if not game:
        return JsonResponse({'status': 'error', 'message': 'No active game'}, status=400)
    
    # Determine Action
    if isinstance(game, TicTacToe):
        if agent == 'manual':
            try:
                action = int(request.GET.get('action'))
            except:
                return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)
        else:
            # AI move
            move_info = minimax(game, 'O', 'O', 'X')
            action = move_info['position']
        
        if action is not None:
            game.make_move(action, 'O' if agent != 'manual' else 'X')
            
            # If AI move was human, then AI move too if game not over
            if agent == 'manual' and not game.get_state()['game_over']:
                ai_move = minimax(game, 'O', 'O', 'X')['position']
                if ai_move is not None:
                    game.make_move(ai_move, 'O')
        
        response_data = game.get_state()
    elif isinstance(game, Game2048):
        if agent == 'manual':
            try:
                action = int(request.GET.get('action'))
                game.move(action)
            except:
                return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)
        else:
            action = game.get_best_move()
            game.move(action)
        response_data = game.get_state()
    elif isinstance(game, Minesweeper):
        if agent == 'manual':
            try:
                r = int(request.GET.get('r'))
                c = int(request.GET.get('c'))
                type = request.GET.get('type', 'reveal')
                if type == 'flag':
                    game.toggle_flag(r, c)
                else:
                    game.reveal(r, c)
            except:
                return JsonResponse({'status': 'error', 'message': 'Invalid coordinates'}, status=400)
        else:
            move = game.get_next_ai_move()
            if move:
                if move['type'] == 'flag':
                    game.toggle_flag(*move['pos'])
                else:
                    game.reveal(*move['pos'])
        response_data = game.get_state()
    elif isinstance(game, Sudoku):
        if agent == 'manual':
            try:
                r = int(request.GET.get('r'))
                c = int(request.GET.get('c'))
                val = int(request.GET.get('val'))
                game.make_move(r, c, val)
            except:
                return JsonResponse({'status': 'error', 'message': 'Invalid move'}, status=400)
        else:
            game.solve_step()
        response_data = game.get_state()
    elif isinstance(game, ConnectFour):
        action = request.GET.get('action')
        if action is not None:
            col = int(action)
            if game.is_valid_location(col):
                game.drop_piece(col, 1)
                if not game.win_check(1) and game.get_valid_locations():
                    ai_col, _ = game.minimax(3, -math.inf, math.inf, True)
                    if ai_col is not None:
                        game.drop_piece(ai_col, 2)
        
        response_data = game.get_state()
        if game.win_check(1):
            response_data['game_over'] = True
            response_data['winner'] = 1
        elif game.win_check(2):
            response_data['game_over'] = True
            response_data['winner'] = 2
        elif not game.get_valid_locations():
            response_data['game_over'] = True
            response_data['winner'] = 0
            
    elif isinstance(game, Othello):
        r = request.GET.get('r')
        c = request.GET.get('c')
        if r is not None and c is not None:
            r, c = int(r), int(c)
            if game.make_move(r, c, 1):
                # AI Turn
                move = game.ai_move()
                if move:
                    game.make_move(move[0], move[1], 2)
        response_data = game.get_state()
    else:
        # Snake Game Logic
        state_before = game.get_state()
        if agent == 'manual':
            try:
                action = int(request.GET.get('action', 1))
            except:
                action = 1
        else:
            action = agent.get_move(state_before)
        
        state_next, reward, done = game.step(action)
        
        if isinstance(agent, QLearningAgent):
            agent.update(state_before, action, reward, state_next, done)
        
        response_data = state_next
        response_data['reward'] = reward
        response_data['action'] = action
        if isinstance(agent, QLearningAgent):
            response_data['weights'] = agent.weights.tolist()
    
    return JsonResponse(response_data)
