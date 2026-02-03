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
from .ai_agent import AIAgent
from .q_learning_agent import QLearningAgent

# Global game and agent instances
valid_games = {}
valid_agents = {} # session_id -> agent_instance

def index(request):
    """Renders the game dashboard."""
    # Get top 10 scores
    top_scores = Score.objects.order_by('-score')[:10]
    
    # Get user's high score
    user_high_score = 0
    if request.user.is_authenticated:
        user_scores = Score.objects.filter(user=request.user).order_by('-score')
        if user_scores.exists():
            user_high_score = user_scores.first().score
            
    return render(request, 'index.html', {
        'top_scores': top_scores, 
        'user_high_score': user_high_score
    })

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

    game = SnakeGame()
    state = game.reset()
    
    # Store in global dict
    session_id = request.session.session_key or 'default'
    if not request.session.session_key:
        request.session.create()
        session_id = request.session.session_key
        
    valid_games[session_id] = game
    
    # Select Agent
    mode = request.GET.get('mode', 'astar') # default to astar
    if mode == 'qlearning':
        # Persist Q-Agent if exists to keep learning? 
        # For this demo, let's keep the agent alive across games if possible
        if session_id not in valid_agents or not isinstance(valid_agents[session_id], QLearningAgent):
             valid_agents[session_id] = QLearningAgent(game)
        else:
             # Just update the game ref
             valid_agents[session_id].game = game
    elif mode == 'manual':
        valid_agents[session_id] = 'manual' # Marker for manual mode
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
        # Try to recover
        game = SnakeGame()
        valid_games[session_id] = game
        agent = AIAgent(game) # Default
        valid_agents[session_id] = agent
    
    state_before = game.get_state()
    
    # Determine Action
    if agent == 'manual':
        # User provides action via request
        try:
            action = int(request.GET.get('action', 1)) # Default to RIGHT if missing
        except:
            action = 1
    else:
        # AI provides action
        action = agent.get_move(state_before)
    
    state_next, reward, done = game.step(action)
    
    # If Q-Learning, train!
    if isinstance(agent, QLearningAgent):
        agent.update(state_before, action, reward, state_next, done)
    
    response_data = state_next
    response_data['reward'] = reward
    response_data['action'] = action
    
    # Return weights if QLearning for visualization
    if isinstance(agent, QLearningAgent):
        response_data['weights'] = agent.weights.tolist()
    
    return JsonResponse(response_data)
