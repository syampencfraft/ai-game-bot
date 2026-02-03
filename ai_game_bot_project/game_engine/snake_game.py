import random
import numpy as np
from enum import Enum

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class SnakeGame:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.reset()

    def reset(self):
        """Resets the game state."""
        self.direction = Direction.RIGHT
        # Snake starts in the middle
        self.head = (self.width // 2, self.height // 2)
        self.body = [self.head, (self.head[0] - 1, self.head[1]), (self.head[0] - 2, self.head[1])]
        self.score = 0
        self.food = self._place_food()
        self.game_over = False
        self.steps = 0
        return self.get_state()

    def set_state(self, state):
        """Restores game state from dictionary."""
        self.width = state['grid_width']
        self.height = state['grid_height']
        self.body = [tuple(x) for x in state['snake']] # Ensure tuples
        self.head = self.body[0]
        self.food = tuple(state['food'])
        self.score = state['score']
        self.game_over = state['game_over']
        # Direction is not explicitly in state dict, assume reasonable default or infer?
        # Ideally, add direction to state. For now, infer or default to RIGHT if unknown.
        # Simple inference:
        if len(self.body) > 1:
            dx = self.head[0] - self.body[1][0]
            dy = self.head[1] - self.body[1][1]
            if dx == 1: self.direction = Direction.RIGHT
            elif dx == -1: self.direction = Direction.LEFT
            elif dy == 1: self.direction = Direction.DOWN
            elif dy == -1: self.direction = Direction.UP
        else:
            self.direction = Direction.RIGHT  

    def _place_food(self):
        """Randomly places food on the grid, ensuring it's not on the snake."""
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in self.body:
                return (x, y)

    def step(self, action):
        """
        Executes a step in the game.
        Action: 0=UP, 1=RIGHT, 2=DOWN, 3=LEFT
        Returns: (state, reward, done)
        """
        if self.game_over:
            return self.get_state(), 0, True

        self.steps += 1
        
        # Prevent 180-degree turns
        clock_wise = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        full_turn = (action + 2) % 4
        
        # If action is opposite to current direction, ignore it (keep moving forward)
        # OR implementation choice: Game Over? Usually in Snake you just can't turn back.
        # Let's enforce: if opposite, keep current direction.
        current_idx = self.direction.value
        if action == (current_idx + 2) % 4:
            action = current_idx # Keep going straight
        
        # Update direction
        self.direction = Direction(action)

        # Move head
        x, y = self.head
        if self.direction == Direction.UP:
            y -= 1
        elif self.direction == Direction.RIGHT:
            x += 1
        elif self.direction == Direction.DOWN:
            y += 1
        elif self.direction == Direction.LEFT:
            x -= 1

        self.head = (x, y)

        # Check collisions
        reward = 0
        if (x < 0 or x >= self.width or y < 0 or y >= self.height or self.head in self.body[:-1]):
            self.game_over = True
            reward = -10 # Penalty for dying
            return self.get_state(), reward, True

        # Check food
        self.body.insert(0, self.head)
        if self.head == self.food:
            self.score += 1
            reward = 10 # Reward for eating
            self.food = self._place_food()
        else:
            self.body.pop()
            # Small penalty for time wasting to encourage efficiency? 
            # For now 0.
            reward = 0

        # Optional: Starvation if too many steps without food?
        
        return self.get_state(), reward, False

    def get_state(self):
        """Returns the current state dictionary."""
        return {
            'grid_width': self.width,
            'grid_height': self.height,
            'snake': self.body,
            'food': self.food,
            'score': self.score,
            'game_over': self.game_over
        }
