"""
Serializers para autenticação e gestão de usuários
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, UserActivity, LGPDConsent


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuários"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    agreed_to_terms = serializers.BooleanField(required=True)
    agreed_to_lgpd = serializers.BooleanField(required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'birth_date', 'phone',
            'agreed_to_terms', 'agreed_to_lgpd', 'marketing_emails',
            'target_exam', 'location'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        
        if not attrs['agreed_to_terms']:
            raise serializers.ValidationError("Você deve aceitar os termos de uso.")
        
        if not attrs['agreed_to_lgpd']:
            raise serializers.ValidationError("Você deve aceitar a política de privacidade.")
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Criar perfil do usuário
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer para login de usuários"""
    
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Credenciais inválidas.')
            
            if not user.is_active:
                raise serializers.ValidationError('Conta desativada.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Email e senha são obrigatórios.')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil do usuário"""
    
    accuracy_rate = serializers.ReadOnlyField()
    is_premium = serializers.ReadOnlyField()
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar', 'bio', 'location', 'target_exam', 'birth_date',
            'total_xp', 'current_level', 'coins', 'gems',
            'current_streak', 'longest_streak', 'daily_goal',
            'subscription_type', 'subscription_expires',
            'accuracy_rate', 'is_premium', 'total_study_time',
            'total_questions_answered', 'correct_answers',
            'is_verified', 'profile', 'created_at'
        ]
        read_only_fields = [
            'id', 'total_xp', 'current_level', 'coins', 'gems',
            'current_streak', 'longest_streak', 'subscription_type',
            'subscription_expires', 'accuracy_rate', 'is_premium',
            'total_study_time', 'total_questions_answered', 
            'correct_answers', 'is_verified', 'created_at'
        ]
    
    def get_profile(self, obj):
        try:
            profile = obj.profile
            return UserProfileDetailSerializer(profile).data
        except UserProfile.DoesNotExist:
            return None


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para perfil estendido"""
    
    class Meta:
        model = UserProfile
        exclude = ['encrypted_cpf', 'encrypted_phone']  # Não expor dados criptografados


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para mudança de senha"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("As novas senhas não coincidem.")
        return attrs


class UserStatsSerializer(serializers.ModelSerializer):
    """Serializer para estatísticas do usuário"""
    
    accuracy_rate = serializers.ReadOnlyField()
    is_premium = serializers.ReadOnlyField()
    study_streak_status = serializers.SerializerMethodField()
    level_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'total_xp', 'current_level', 'coins', 'gems',
            'current_streak', 'longest_streak', 'accuracy_rate',
            'total_study_time', 'total_questions_answered',
            'correct_answers', 'is_premium', 'study_streak_status',
            'level_progress'
        ]
    
    def get_study_streak_status(self, obj):
        """Status do streak de estudos"""
        from django.utils import timezone
        
        if obj.last_study_date:
            days_since_last = (timezone.now().date() - obj.last_study_date).days
            if days_since_last == 0:
                return "active_today"
            elif days_since_last == 1:
                return "at_risk"
            else:
                return "broken"
        return "no_streak"
    
    def get_level_progress(self, obj):
        """Progresso para o próximo nível"""
        current_level_xp = sum(100 * i for i in range(1, obj.current_level + 1))
        next_level_xp = sum(100 * i for i in range(1, obj.current_level + 2))
        
        progress_in_level = obj.total_xp - current_level_xp
        level_total_xp = next_level_xp - current_level_xp
        
        return {
            'current_level': obj.current_level,
            'progress_xp': progress_in_level,
            'level_total_xp': level_total_xp,
            'progress_percentage': (progress_in_level / level_total_xp) * 100 if level_total_xp > 0 else 0,
            'xp_to_next_level': level_total_xp - progress_in_level
        }


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer para atividades do usuário"""
    
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'activity_type', 'activity_type_display',
            'description', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LGPDConsentSerializer(serializers.ModelSerializer):
    """Serializer para consentimentos LGPD"""
    
    consent_type_display = serializers.CharField(source='get_consent_type_display', read_only=True)
    
    class Meta:
        model = LGPDConsent
        fields = [
            'id', 'consent_type', 'consent_type_display',
            'granted', 'granted_at', 'terms_version'
        ]
        read_only_fields = ['id', 'granted_at']


class DataExportSerializer(serializers.Serializer):
    """Serializer para exportação de dados LGPD"""
    
    include_profile = serializers.BooleanField(default=True)
    include_activities = serializers.BooleanField(default=True)
    include_progress = serializers.BooleanField(default=True)
    include_purchases = serializers.BooleanField(default=False)
    format = serializers.ChoiceField(choices=['json', 'csv'], default='json')


# Serializers para ViewSets
class UserViewSetSerializer(serializers.ModelSerializer):
    """Serializer básico para ViewSet de usuários"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar', 'current_level', 'total_xp', 'is_verified'
        ]
        read_only_fields = ['id', 'current_level', 'total_xp', 'is_verified']


class UserProfileViewSetSerializer(serializers.ModelSerializer):
    """Serializer para ViewSet de perfis de usuário"""
    
    class Meta:
        model = UserProfile
        fields = [
            'favorite_subjects', 'weak_subjects', 'study_goals',
            'push_notifications', 'email_notifications', 'streak_reminders'
        ] 