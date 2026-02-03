from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('start-game/', views.start_game, name='start_game'),
    path('step/', views.game_step, name='game_step'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('save-score/', views.save_score, name='save_score'),
]
