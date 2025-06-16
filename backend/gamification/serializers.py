"""
Serializers para o sistema de gamificação do Duolingo Jurídico
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    Achievement, UserAchievement, Leaderboard, LeaderboardEntry,
    StoreItem, UserPurchase, UserBoost, DailyChallenge,
    DailyChallengeCompletion
)

User = get_user_model()


class AchievementSerializer(serializers.ModelSerializer):
    """Serializer para conquistas"""
    
    user_unlocked = serializers.SerializerMethodField()
    unlock_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Achievement
        fields = [
            'id', 'name', 'description', 'achievement_type', 'rarity',
            'requirements', 'xp_reward', 'coin_reward', 'gem_reward',
            'icon', 'badge_color', 'is_active', 'is_secret', 'unlock_count',
            'user_unlocked', 'unlock_progress', 'created_at'
        ]
        read_only_fields = ['unlock_count', 'created_at']
    
    def get_user_unlocked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserAchievement.objects.filter(
                user=request.user,
                achievement=obj
            ).exists()
        return False
    
    def get_unlock_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Calcular progresso baseado nos requisitos
            user = request.user
            reqs = obj.requirements
            
            if obj.achievement_type == 'streak':
                target = reqs.get('days', 1)
                current = user.current_streak
                return {
                    'current': current,
                    'target': target,
                    'percentage': min(100, (current / target) * 100)
                }
            
            elif obj.achievement_type == 'xp':
                target = reqs.get('total_xp', 100)
                current = user.total_xp
                return {
                    'current': current,
                    'target': target,
                    'percentage': min(100, (current / target) * 100)
                }
            
            elif obj.achievement_type == 'lessons':
                target = reqs.get('total_lessons', 10)
                current = user.user_lessons.filter(completed=True).count()
                return {
                    'current': current,
                    'target': target,
                    'percentage': min(100, (current / target) * 100)
                }
        
        return {'current': 0, 'target': 1, 'percentage': 0}


class UserAchievementSerializer(serializers.ModelSerializer):
    """Serializer para conquistas desbloqueadas"""
    
    achievement_name = serializers.CharField(source='achievement.name', read_only=True)
    achievement_description = serializers.CharField(source='achievement.description', read_only=True)
    achievement_rarity = serializers.CharField(source='achievement.rarity', read_only=True)
    achievement_icon = serializers.ImageField(source='achievement.icon', read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = [
            'id', 'achievement', 'achievement_name', 'achievement_description',
            'achievement_rarity', 'achievement_icon', 'unlocked_at',
            'progress_when_unlocked', 'xp_received', 'coins_received', 'gems_received'
        ]
        read_only_fields = [
            'unlocked_at', 'xp_received', 'coins_received', 'gems_received'
        ]


class LeaderboardEntrySerializer(serializers.ModelSerializer):
    """Serializer para entradas do ranking"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    
    class Meta:
        model = LeaderboardEntry
        fields = [
            'id', 'user', 'user_name', 'username', 'user_avatar',
            'position', 'score', 'previous_position', 'position_change',
            'period_start', 'period_end', 'created_at'
        ]
        read_only_fields = ['position_change', 'created_at']


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer para rankings"""
    
    entries = LeaderboardEntrySerializer(many=True, read_only=True)
    user_position = serializers.SerializerMethodField()
    
    class Meta:
        model = Leaderboard
        fields = [
            'id', 'name', 'leaderboard_type', 'period', 'subject_filter',
            'max_entries', 'is_active', 'current_period_start',
            'current_period_end', 'last_updated', 'entries', 'user_position',
            'created_at'
        ]
        read_only_fields = ['last_updated', 'created_at']
    
    def get_user_position(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                entry = obj.entries.get(user=request.user)
                return {
                    'position': entry.position,
                    'score': entry.score,
                    'position_change': entry.position_change
                }
            except LeaderboardEntry.DoesNotExist:
                return None
        return None


class StoreItemSerializer(serializers.ModelSerializer):
    """Serializer para itens da loja"""
    
    user_owned = serializers.SerializerMethodField()
    can_purchase = serializers.SerializerMethodField()
    
    class Meta:
        model = StoreItem
        fields = [
            'id', 'name', 'description', 'item_type', 'coin_price',
            'gem_price', 'real_price', 'image', 'preview_image',
            'item_data', 'duration_hours', 'is_active', 'is_limited',
            'stock_quantity', 'available_from', 'available_until',
            'purchase_count', 'is_available', 'user_owned', 'can_purchase',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['purchase_count', 'created_at', 'updated_at']
    
    def get_user_owned(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserPurchase.objects.filter(
                user=request.user,
                item=obj,
                status='completed'
            ).exists()
        return False
    
    def get_can_purchase(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        user = request.user
        
        # Verificar se está disponível
        if not obj.is_available:
            return False
        
        # Verificar se já possui (para itens únicos)
        if obj.item_type in ['avatar', 'theme'] and self.get_user_owned(obj):
            return False
        
        # Verificar se tem moedas/gemas suficientes
        if obj.coin_price and user.total_coins < obj.coin_price:
            return False
        
        if obj.gem_price and user.total_gems < obj.gem_price:
            return False
        
        return True


class UserPurchaseSerializer(serializers.ModelSerializer):
    """Serializer para compras dos usuários"""
    
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_image = serializers.ImageField(source='item.image', read_only=True)
    
    class Meta:
        model = UserPurchase
        fields = [
            'id', 'item', 'item_name', 'item_image', 'quantity',
            'payment_method', 'coins_spent', 'gems_spent', 'real_amount',
            'status', 'external_transaction_id', 'purchased_at', 'completed_at'
        ]
        read_only_fields = [
            'status', 'external_transaction_id', 'purchased_at', 'completed_at'
        ]
    
    def create(self, validated_data):
        # Garantir que o usuário é o da requisição
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserBoostSerializer(serializers.ModelSerializer):
    """Serializer para impulsos ativos"""
    
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = UserBoost
        fields = [
            'id', 'boost_type', 'activated_at', 'expires_at',
            'duration_hours', 'is_active', 'is_expired', 'time_remaining'
        ]
        read_only_fields = ['activated_at', 'is_expired']
    
    def get_time_remaining(self, obj):
        if obj.is_expired:
            return 0
        
        remaining = obj.expires_at - timezone.now()
        return max(0, remaining.total_seconds())


class DailyChallengeSerializer(serializers.ModelSerializer):
    """Serializer para desafios diários"""
    
    user_progress = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = DailyChallenge
        fields = [
            'id', 'title', 'description', 'challenge_type', 'difficulty',
            'target_value', 'conditions', 'xp_reward', 'gems_reward',
            'additional_rewards', 'date', 'is_active', 'total_participants',
            'completion_rate', 'user_progress', 'is_completed', 'created_at'
        ]
        read_only_fields = ['total_participants', 'completion_rate', 'created_at']
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                completion = DailyChallengeCompletion.objects.get(
                    challenge=obj,
                    user=request.user
                )
                return {
                    'current_progress': completion.current_progress,
                    'target': obj.target_value,
                    'percentage': completion.completion_percentage,
                    'status': completion.status
                }
            except DailyChallengeCompletion.DoesNotExist:
                return {
                    'current_progress': 0,
                    'target': obj.target_value,
                    'percentage': 0,
                    'status': 'not_started'
                }
        return None
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return DailyChallengeCompletion.objects.filter(
                challenge=obj,
                user=request.user,
                status='completed'
            ).exists()
        return False


class GamificationStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas de gamificação"""
    
    # XP e níveis
    total_xp = serializers.IntegerField()
    current_level = serializers.IntegerField()
    xp_for_next_level = serializers.IntegerField()
    level_progress_percentage = serializers.FloatField()
    
    # Moedas e gemas
    total_coins = serializers.IntegerField()
    total_gems = serializers.IntegerField()
    
    # Streaks
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    
    # Conquistas
    total_achievements = serializers.IntegerField()
    achievements_by_rarity = serializers.JSONField()
    
    # Rankings
    best_ranking_position = serializers.IntegerField()
    current_rankings = serializers.JSONField()
    
    # Atividade
    lessons_completed = serializers.IntegerField()
    quizzes_completed = serializers.IntegerField()
    accuracy_rate = serializers.FloatField()


class AchievementListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de conquistas"""
    
    user_unlocked = serializers.SerializerMethodField()
    
    class Meta:
        model = Achievement
        fields = [
            'id', 'name', 'description', 'rarity', 'icon',
            'badge_color', 'user_unlocked'
        ]
    
    def get_user_unlocked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserAchievement.objects.filter(
                user=request.user,
                achievement=obj
            ).exists()
        return False


class StoreItemListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de itens da loja"""
    
    class Meta:
        model = StoreItem
        fields = [
            'id', 'name', 'item_type', 'coin_price', 'gem_price',
            'real_price', 'image', 'is_available'
        ]


class LeaderboardListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de rankings"""
    
    class Meta:
        model = Leaderboard
        fields = [
            'id', 'name', 'leaderboard_type', 'period',
            'current_period_start', 'current_period_end'
        ]


class DailyChallengeCompletionSerializer(serializers.ModelSerializer):
    """Serializer para conclusão de desafios diários"""
    
    challenge = DailyChallengeSerializer(read_only=True)
    completion_percentage = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = DailyChallengeCompletion
        fields = [
            'id', 'challenge', 'user', 'user_name',
            'status', 'current_progress', 'completion_percentage',
            'progress_data', 'rewards_claimed',
            'started_at', 'completed_at'
        ]
        read_only_fields = ['user', 'started_at'] 