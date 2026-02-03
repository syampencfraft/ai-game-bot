
import random
import numpy as np
from game_engine.snake_game import Direction

class QLearningAgent:
    def __init__(self, game):
        self.game = game
        # Weights for features: [bias, food_dist, free_space, danger]
        # Initial weights can be random or zero. 
        # Tuning: 
        # w0 (bias): 0
        # w1 (food_dist): negative (closer is better)
        # w2 (free_space_adj): positive (more space is better)
        # w3 (danger): negative (large penalty)
        self.weights = np.array([0.0, -2.0, 0.1, -100.0]) 
        self.epsilon = 0.1 # Exploration rate (0.0 means greedy)
        self.alpha = 0.01  # Learning rate
        self.gamma = 0.9   # Discount factor

    def get_features(self, state, action):
        """
        Extracts features for a (state, action) pair.
        We simulate the next state to extract features.
        """
        # We need to simulate the move. simpler to query game for "what if"
        # Since game is stateful, we can peek.
        
        head = state['snake'][0]
        food = state['food']
        obstacles = set(state['snake'][:-1]) # Body parts
        
        # Determine next position based on action
        x, y = head
        if action == Direction.UP.value: y -= 1
        elif action == Direction.RIGHT.value: x += 1
        elif action == Direction.DOWN.value: y += 1
        elif action == Direction.LEFT.value: x -= 1
        
        next_pos = (x, y)
        
        # Feature 1: Bias
        f0 = 1.0
        
        # Feature 2: Distance to food (Manhattan)
        dist = abs(next_pos[0] - food[0]) + abs(next_pos[1] - food[1])
        f1 = dist
        
        # Feature 3: Danger (is next_pos invalid?)
        is_danger = 0.0
        if (x < 0 or x >= state['grid_width'] or 
            y < 0 or y >= state['grid_height'] or 
            next_pos in obstacles):
            is_danger = 1.0
        f2 = is_danger
        
        # Feature 3 (New): Adjacent Free Space (heuristic)
        # Count free neighbors of next_pos (if not danger)
        f3 = 0.0
        if not is_danger:
            neighbors = [
                (x+1, y), (x-1, y), (x, y+1), (x, y-1)
            ]
            for nx, ny in neighbors:
                if (0 <= nx < state['grid_width'] and 
                    0 <= ny < state['grid_height'] and 
                    (nx, ny) not in obstacles):
                    f3 += 1.0
                    
        return np.array([f0, f1, f3, f2])

    def get_q_value(self, state, action):
        features = self.get_features(state, action)
        return np.dot(self.weights, features)

    def get_move(self, state=None):
        if state is None:
            state = self.game.get_state()

        # Epsilon-greedy
        if random.random() < self.epsilon:
            return random.randint(0, 3)
        
        # Best action
        q_values = [self.get_q_value(state, a) for a in range(4)]
        max_q = max(q_values)
        
        # Random tie breaking
        best_actions = [i for i, q in enumerate(q_values) if q == max_q]
        return random.choice(best_actions)

    def update(self, state, action, reward, next_state, done):
        """
        Updates weights based on experience.
        """
        if done:
            target = reward
        else:
            next_q_values = [self.get_q_value(next_state, a) for a in range(4)]
            target = reward + self.gamma * max(next_q_values)
            
        current_q = self.get_q_value(state, action)
        difference = target - current_q
        
        features = self.get_features(state, action)
        
        # Gradient descent update: w = w + alpha * difference * features
        self.weights += self.alpha * difference * features
