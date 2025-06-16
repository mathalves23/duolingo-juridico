"""
URLs do sistema social
"""

from django.urls import path
from . import views

urlpatterns = [
    # Busca de usuários
    path('search/', views.search_users, name='search-users'),
    
    # Sistema de seguir/deixar de seguir
    path('follow/<int:user_id>/', views.follow_user, name='follow-user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow-user'),
    
    # Sistema de amizades
    path('friend-request/<int:user_id>/', views.send_friend_request, name='send-friend-request'),
    path('accept-friend/<int:user_id>/', views.accept_friend_request, name='accept-friend-request'),
    path('reject-friend/<int:user_id>/', views.reject_friend_request, name='reject-friend-request'),
    
    # Listas sociais
    path('friends/', views.list_friends, name='list-friends'),
    path('followers/', views.list_followers, name='list-followers'),
    path('following/', views.list_following, name='list-following'),
    path('friend-requests/', views.friend_requests, name='friend-requests'),
    
    # Feed e estatísticas
    path('feed/', views.social_feed, name='social-feed'),
    path('stats/', views.social_stats, name='social-stats'),
]
