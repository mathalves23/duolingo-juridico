"""
Serializers para o sistema de cursos do Duolingo Jurídico
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Subject, Topic, Lesson, UserLesson, 
    LegalContent, StudyPath, StudyPathSubject, UserStudyPath
)

User = get_user_model()


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer para disciplinas"""
    
    total_topics = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = [
            'id', 'name', 'category', 'description', 'icon', 'color_hex',
            'order', 'is_active', 'is_premium', 'total_lessons', 
            'estimated_hours', 'total_topics', 'user_progress',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total_lessons', 'created_at', 'updated_at']
    
    def get_total_topics(self, obj):
        return obj.topics.count()
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Calcular progresso do usuário nesta disciplina
            total_lessons = Lesson.objects.filter(topic__subject=obj).count()
            if total_lessons == 0:
                return 0.0
            
            completed_lessons = UserLesson.objects.filter(
                user=request.user,
                lesson__topic__subject=obj,
                completed=True
            ).count()
            
            return round((completed_lessons / total_lessons) * 100, 2)
        return 0.0


class TopicSerializer(serializers.ModelSerializer):
    """Serializer para tópicos"""
    
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subtopics_count = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    is_unlocked = serializers.SerializerMethodField()
    
    class Meta:
        model = Topic
        fields = [
            'id', 'name', 'description', 'subject', 'subject_name',
            'parent_topic', 'order', 'is_active', 'is_premium',
            'requires_previous_completion', 'total_lessons', 'estimated_minutes',
            'subtopics_count', 'lessons_count', 'user_progress', 'is_unlocked',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total_lessons', 'created_at', 'updated_at']
    
    def get_subtopics_count(self, obj):
        return obj.subtopics.count()
    
    def get_lessons_count(self, obj):
        return obj.lessons.count()
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            total_lessons = obj.lessons.count()
            if total_lessons == 0:
                return 0.0
            
            completed_lessons = UserLesson.objects.filter(
                user=request.user,
                lesson__topic=obj,
                completed=True
            ).count()
            
            return round((completed_lessons / total_lessons) * 100, 2)
        return 0.0
    
    def get_is_unlocked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        # Se não requer conclusão anterior, está desbloqueado
        if not obj.requires_previous_completion:
            return True
        
        # Verificar se o tópico anterior foi completado
        if obj.parent_topic:
            return self.get_user_progress(obj.parent_topic) >= 80.0
        
        # Primeiro tópico da disciplina está sempre desbloqueado
        return True


class LessonSerializer(serializers.ModelSerializer):
    """Serializer para lições"""
    
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    subject_name = serializers.CharField(source='topic.subject.name', read_only=True)
    user_progress = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    user_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'topic', 'topic_name', 'subject_name',
            'lesson_type', 'difficulty_level', 'content', 'legal_references',
            'order', 'is_active', 'is_premium', 'xp_reward', 'coin_reward',
            'estimated_minutes', 'completion_count', 'average_score',
            'content_version', 'last_legal_update', 'user_progress',
            'is_completed', 'user_score', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'completion_count', 'average_score', 'content_version',
            'last_legal_update', 'created_at', 'updated_at'
        ]
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                user_lesson = UserLesson.objects.get(
                    user=request.user,
                    lesson=obj
                )
                return user_lesson.score
            except UserLesson.DoesNotExist:
                return 0.0
        return 0.0
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserLesson.objects.filter(
                user=request.user,
                lesson=obj,
                completed=True
            ).exists()
        return False
    
    def get_user_score(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                user_lesson = UserLesson.objects.get(
                    user=request.user,
                    lesson=obj
                )
                return user_lesson.score
            except UserLesson.DoesNotExist:
                return 0.0
        return 0.0


class UserLessonSerializer(serializers.ModelSerializer):
    """Serializer para progresso do usuário em lições"""
    
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    topic_name = serializers.CharField(source='lesson.topic.name', read_only=True)
    subject_name = serializers.CharField(source='lesson.topic.subject.name', read_only=True)
    
    class Meta:
        model = UserLesson
        fields = [
            'id', 'lesson', 'lesson_title', 'topic_name', 'subject_name',
            'started_at', 'completed_at', 'completed', 'score', 'attempts',
            'xp_earned', 'coins_earned', 'next_review_date', 
            'review_interval_days', 'ease_factor'
        ]
        read_only_fields = ['started_at', 'xp_earned', 'coins_earned']
    
    def create(self, validated_data):
        # Garantir que o usuário é o da requisição
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class LegalContentSerializer(serializers.ModelSerializer):
    """Serializer para conteúdo jurídico"""
    
    subjects_names = serializers.StringRelatedField(source='subjects', many=True, read_only=True)
    
    class Meta:
        model = LegalContent
        fields = [
            'id', 'title', 'content_type', 'official_number',
            'publication_date', 'effective_date', 'full_text', 'summary',
            'source_url', 'subjects', 'subjects_names', 'version', 
            'is_current', 'replaced_by', 'last_checked', 'auto_update',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['last_checked', 'created_at', 'updated_at']


class StudyPathSubjectSerializer(serializers.ModelSerializer):
    """Serializer para disciplinas em trilhas de estudo"""
    
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_color = serializers.CharField(source='subject.color_hex', read_only=True)
    
    class Meta:
        model = StudyPathSubject
        fields = [
            'id', 'subject', 'subject_name', 'subject_color',
            'order', 'weight', 'estimated_hours'
        ]


class StudyPathSerializer(serializers.ModelSerializer):
    """Serializer para trilhas de estudo"""
    
    subjects_detail = StudyPathSubjectSerializer(
        source='studypathsubject_set', 
        many=True, 
        read_only=True
    )
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = StudyPath
        fields = [
            'id', 'name', 'description', 'target_exam', 'subjects',
            'subjects_detail', 'estimated_weeks', 'difficulty_level',
            'is_public', 'is_premium', 'created_by', 'created_by_name',
            'enrollment_count', 'completion_rate', 'is_enrolled',
            'user_progress', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'enrollment_count', 'completion_rate', 'created_at', 'updated_at'
        ]
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserStudyPath.objects.filter(
                user=request.user,
                study_path=obj
            ).exists()
        return False
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                enrollment = UserStudyPath.objects.get(
                    user=request.user,
                    study_path=obj
                )
                return enrollment.progress_percentage
            except UserStudyPath.DoesNotExist:
                return 0.0
        return 0.0


class UserStudyPathSerializer(serializers.ModelSerializer):
    """Serializer para matrículas em trilhas de estudo"""
    
    study_path_name = serializers.CharField(source='study_path.name', read_only=True)
    current_subject_name = serializers.CharField(source='current_subject.name', read_only=True)
    
    class Meta:
        model = UserStudyPath
        fields = [
            'id', 'study_path', 'study_path_name', 'enrolled_at',
            'target_completion_date', 'current_subject', 'current_subject_name',
            'progress_percentage', 'completed', 'completed_at'
        ]
        read_only_fields = ['enrolled_at', 'progress_percentage', 'completed_at']
    
    def create(self, validated_data):
        # Garantir que o usuário é o da requisição
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# Serializers simplificados para listagens
class SubjectListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de disciplinas"""
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'category', 'icon', 'color_hex', 'is_premium']


class TopicListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de tópicos"""
    
    class Meta:
        model = Topic
        fields = ['id', 'name', 'order', 'is_premium', 'total_lessons']


class LessonListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de lições"""
    
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'lesson_type', 'difficulty_level',
            'order', 'is_premium', 'xp_reward', 'estimated_minutes',
            'is_completed'
        ]
    
    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserLesson.objects.filter(
                user=request.user,
                lesson=obj,
                completed=True
            ).exists()
        return False 