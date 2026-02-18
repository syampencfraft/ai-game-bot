import heapq
import random
from game_engine.snake_game import Direction

class AIAgent:
    def __init__(self, game):
        self.game = game

    def get_move(self, state=None):
        """
        Determines the next move for the snake.
        Returns: Action (0, 1, 2, 3)
        """
        if state is None:
            state = self.game.get_state()

        start = tuple(state['snake'][0])
        goal = tuple(state['food'])
        
        # Grid boundaries
        rows, cols = state['grid_height'], state['grid_width']
        # Obstacles = snake body (excluding tail because it moves)
        obstacles = set(tuple(p) for p in state['snake'][:-1]) 
        
        # A* Search
        path = self._a_star_search(start, goal, obstacles, rows, cols)
        
        if path and len(path) > 1:
            # Determine direction from partial path (start -> next_node)
            next_node = path[1]
            return self._get_direction(start, next_node)
        
        # Fallback: Random valid move if no path to food found
        return self._get_fallback_move(start, obstacles, rows, cols)

    def _a_star_search(self, start, goal, obstacles, rows, cols):
        """
        A* algorithm to find the shortest path from start to goal.
        """
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, goal)}
        
        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current == goal:
                return self._reconstruct_path(came_from, current)
            
            for neighbor in self._get_neighbors(current, rows, cols):
                if neighbor in obstacles:
                    continue
                
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self._heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    
        return None # No path found

    def _heuristic(self, a, b):
        """Manhattan distance."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _get_neighbors(self, node, rows, cols):
        x, y = node
        neighbors = [
            (x+1, y), (x-1, y), (x, y+1), (x, y-1)
        ]
        return [(nx, ny) for nx, ny in neighbors if 0 <= nx < cols and 0 <= ny < rows]

    def _reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1] # Reverse

    def _get_direction(self, start, next_node):
        dx = next_node[0] - start[0]
        dy = next_node[1] - start[1]
        
        if dx == 1: return Direction.RIGHT.value
        if dx == -1: return Direction.LEFT.value
        if dy == 1: return Direction.DOWN.value
        if dy == -1: return Direction.UP.value
        return Direction.RIGHT.value # Default

    def _get_fallback_move(self, start, obstacles, rows, cols):
        """Returns any valid move that doesn't kill the snake adjacent."""
        valid_moves = []
        for d_enum in Direction:
            idx = d_enum.value
            # Predict next pos
            x, y = start
            if d_enum == Direction.UP: y -= 1
            elif d_enum == Direction.RIGHT: x += 1
            elif d_enum == Direction.DOWN: y += 1
            elif d_enum == Direction.LEFT: x -= 1
            
            if 0 <= x < cols and 0 <= y < rows and (x, y) not in obstacles:
                valid_moves.append(idx)
        
        if valid_moves:
            return random.choice(valid_moves)
        
        # If no valid moves, just go forward and die
        return Direction.RIGHT.value
