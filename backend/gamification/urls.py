"""
URLs para gamificação
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AchievementViewSet, UserAchievementViewSet,
    LeaderboardViewSet, StoreItemViewSet, UserPurchaseViewSet,
    UserBoostViewSet, DailyChallengeViewSet, DailyChallengeCompletionViewSet,
    GamificationStatsView
)

router = DefaultRouter()

# Registrar ViewSets
router.register(r'achievements', AchievementViewSet, basename='achievement')
router.register(r'user-achievements', UserAchievementViewSet, basename='user-achievement')
router.register(r'leaderboards', LeaderboardViewSet, basename='leaderboard')
router.register(r'store-items', StoreItemViewSet, basename='store-item')
router.register(r'user-purchases', UserPurchaseViewSet, basename='user-purchase')
router.register(r'user-boosts', UserBoostViewSet, basename='user-boost')
router.register(r'daily-challenges', DailyChallengeViewSet, basename='daily-challenge')
router.register(r'daily-challenge-completions', DailyChallengeCompletionViewSet, basename='daily-challenge-completion')
router.register(r'stats', GamificationStatsView, basename='gamification-stats')

urlpatterns = [
    path('', include(router.urls)),
] 