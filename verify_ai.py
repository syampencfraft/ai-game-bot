
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'ai_game_bot_project')))

from game_engine.snake_game import SnakeGame
from game_engine.ai_agent import AIAgent

def main():
    game = SnakeGame(width=10, height=10)
    ai = AIAgent(game)
    
    print("Initial State:")
    print(game.get_state())
    
    for i in range(20):
        action = ai.get_move()
        state, reward, done = game.step(action)
        print(f"Step {i+1}: Action={action}, Head={game.head}, Food={game.food}, Reward={reward}, Done={done}")
        if done:
            print("Game Over!")
            break

if __name__ == "__main__":
    main()
