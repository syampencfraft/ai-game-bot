from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('games/snake/', views.snake_view, name='snake'),
    path('games/tictactoe/', views.tictactoe_view, name='tictactoe'),
    path('games/2048/', views.game2048_view, name='game2048'),
    path('games/minesweeper/', views.minesweeper_view, name='minesweeper'),
    path('games/sudoku/', views.sudoku_view, name='sudoku'),
    path('games/connect_four/', views.connect_four_view, name='connect_four'),
    path('games/othello/', views.othello_view, name='othello'),
    
    path('start-game/', views.start_game, name='start_game'),
    path('step/', views.game_step, name='game_step'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('save-score/', views.save_score, name='save_score'),
]
