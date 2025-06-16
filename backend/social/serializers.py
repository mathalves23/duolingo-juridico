"""
Serializers do sistema social
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import UserProfile, UserActivity


class UserSearchSerializer(serializers.ModelSerializer):
    """Serializer para busca de usuários"""
    profile = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_friend = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'profile', 'is_following', 'is_friend']
    
    def get_profile(self, obj):
        try:
            profile = UserProfile.objects.get(user=obj)
            return {
                'level': profile.level,
                'xp': profile.xp,
                'streak': profile.streak,
                'subscription_type': profile.subscription_type
            }
        except UserProfile.DoesNotExist:
            return None
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                current_profile = UserProfile.objects.get(user=request.user)
                following = getattr(current_profile, 'following', [])
                return obj.id in following
            except UserProfile.DoesNotExist:
                return False
        return False
    
    def get_is_friend(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                current_profile = UserProfile.objects.get(user=request.user)
                friends = getattr(current_profile, 'friends', [])
                return obj.id in friends
            except UserProfile.DoesNotExist:
                return False
        return False


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil de usuário"""
    profile = serializers.SerializerMethodField()
    social_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile', 'social_stats']
    
    def get_profile(self, obj):
        try:
            profile = UserProfile.objects.get(user=obj)
            return {
                'level': profile.level,
                'xp': profile.xp,
                'streak': profile.streak,
                'subscription_type': profile.subscription_type,
                'last_activity': profile.last_activity
            }
        except UserProfile.DoesNotExist:
            return None
    
    def get_social_stats(self, obj):
        try:
            profile = UserProfile.objects.get(user=obj)
            return {
                'friends_count': len(getattr(profile, 'friends', [])),
                'followers_count': len(getattr(profile, 'followers', [])),
                'following_count': len(getattr(profile, 'following', []))
            }
        except UserProfile.DoesNotExist:
            return {
                'friends_count': 0,
                'followers_count': 0,
                'following_count': 0
            }


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer para atividades do usuário"""
    user_info = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = UserActivity
        fields = ['id', 'user_info', 'activity_type', 'description', 'points_earned', 
                 'metadata', 'created_at', 'time_ago']
    
    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name
        }
    
    def get_time_ago(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "agora mesmo"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} min atrás"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h atrás"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days}d atrás"
        else:
            return obj.created_at.strftime("%d/%m/%Y")


class SocialStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas sociais"""
    friends_count = serializers.IntegerField()
    followers_count = serializers.IntegerField()
    following_count = serializers.IntegerField()
    friend_requests_received = serializers.IntegerField()
    friend_requests_sent = serializers.IntegerField()
