"""
Serializers para o sistema de questões e simulados do Duolingo Jurídico
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ExamBoard, Question, QuestionOption, QuestionExplanation,
    UserAnswer, Quiz, QuizAttempt, QuestionReport
)

User = get_user_model()


class ExamBoardSerializer(serializers.ModelSerializer):
    """Serializer para bancas examinadoras"""
    
    class Meta:
        model = ExamBoard
        fields = [
            'id', 'name', 'acronym', 'description', 'website', 'logo',
            'total_questions', 'difficulty_average', 'is_active', 'created_at'
        ]
        read_only_fields = ['total_questions', 'difficulty_average', 'created_at']


class QuestionOptionSerializer(serializers.ModelSerializer):
    """Serializer para alternativas de questões"""
    
    class Meta:
        model = QuestionOption
        fields = ['id', 'letter', 'text', 'is_correct', 'explanation', 'order']
        
    def to_representation(self, instance):
        """Ocultar is_correct se não for administrador"""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Se não é admin e a questão ainda não foi respondida, ocultar gabarito
        if request and not request.user.is_staff:
            # Verificar se o usuário já respondeu esta questão
            user_answered = hasattr(request.user, 'user_answers') and \
                           request.user.user_answers.filter(
                               question=instance.question
                           ).exists()
            
            if not user_answered:
                data.pop('is_correct', None)
        
        return data


class QuestionExplanationSerializer(serializers.ModelSerializer):
    """Serializer para explicações de questões"""
    
    class Meta:
        model = QuestionExplanation
        fields = [
            'id', 'general_explanation', 'options_explanation',
            'legal_articles', 'jurisprudence_references', 'doctrine_citations',
            'solution_tips', 'common_mistakes', 'ai_generated', 'ai_confidence',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['ai_generated', 'ai_confidence', 'created_at', 'updated_at']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer para questões"""
    
    options = QuestionOptionSerializer(many=True, read_only=True)
    explanation = QuestionExplanationSerializer(read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    exam_board_name = serializers.CharField(source='exam_board.acronym', read_only=True)
    
    # Campos calculados
    user_answered = serializers.SerializerMethodField()
    user_correct = serializers.SerializerMethodField()
    user_answer_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id', 'title', 'statement', 'question_type', 'difficulty_level',
            'subject', 'subject_name', 'topic', 'topic_name', 
            'exam_board', 'exam_board_name', 'exam_name', 'exam_year',
            'exam_date', 'source_url', 'legal_references', 'related_jurisprudence',
            'doctrine_explanation', 'tags', 'estimated_time_seconds',
            'times_answered', 'correct_answers', 'average_time', 'accuracy_rate',
            'is_active', 'is_premium', 'reviewed', 'options', 'explanation',
            'user_answered', 'user_correct', 'user_answer_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'times_answered', 'correct_answers', 'average_time', 'accuracy_rate',
            'created_at', 'updated_at'
        ]
    
    def get_user_answered(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserAnswer.objects.filter(
                user=request.user,
                question=obj
            ).exists()
        return False
    
    def get_user_correct(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                user_answer = UserAnswer.objects.get(
                    user=request.user,
                    question=obj
                )
                return user_answer.is_correct
            except UserAnswer.DoesNotExist:
                return None
        return None
    
    def get_user_answer_time(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                user_answer = UserAnswer.objects.get(
                    user=request.user,
                    question=obj
                )
                return user_answer.time_spent
            except UserAnswer.DoesNotExist:
                return None
        return None


class QuestionListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de questões"""
    
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    exam_board_name = serializers.CharField(source='exam_board.acronym', read_only=True)
    user_answered = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id', 'title', 'question_type', 'difficulty_level',
            'subject_name', 'exam_board_name', 'exam_year', 'accuracy_rate',
            'is_premium', 'user_answered'
        ]
    
    def get_user_answered(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserAnswer.objects.filter(
                user=request.user,
                question=obj
            ).exists()
        return False


class UserAnswerSerializer(serializers.ModelSerializer):
    """Serializer para respostas dos usuários"""
    
    question_title = serializers.CharField(source='question.title', read_only=True)
    selected_option_text = serializers.CharField(source='selected_option.text', read_only=True)
    
    class Meta:
        model = UserAnswer
        fields = [
            'id', 'question', 'question_title', 'selected_option', 
            'selected_option_text', 'text_answer', 'is_correct', 'score',
            'time_spent', 'attempts', 'answered_in_lesson', 'answered_in_quiz',
            'ai_feedback', 'feedback_requested', 'answered_at'
        ]
        read_only_fields = ['is_correct', 'score', 'ai_feedback', 'answered_at']
    
    def create(self, validated_data):
        # Garantir que o usuário é o da requisição
        validated_data['user'] = self.context['request'].user
        
        # Avaliar a resposta
        question = validated_data['question']
        selected_option = validated_data.get('selected_option')
        
        if selected_option:
            validated_data['is_correct'] = selected_option.is_correct
            validated_data['score'] = 100.0 if selected_option.is_correct else 0.0
        else:
            # Para questões dissertativas, marcar para revisão manual
            validated_data['is_correct'] = False
            validated_data['score'] = 0.0
        
        return super().create(validated_data)


class QuizSerializer(serializers.ModelSerializer):
    """Serializer para quizzes e simulados"""
    
    subjects_names = serializers.StringRelatedField(source='subjects', many=True, read_only=True)
    exam_board_name = serializers.CharField(source='exam_board.acronym', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    # Estatísticas do usuário
    user_attempts = serializers.SerializerMethodField()
    user_best_score = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'quiz_type', 'status',
            'subjects', 'subjects_names', 'exam_board', 'exam_board_name',
            'time_limit_minutes', 'max_questions', 'difficulty_level',
            'min_year', 'max_year', 'xp_reward', 'coin_reward',
            'is_premium', 'is_public', 'total_attempts', 'average_score',
            'average_time', 'created_by', 'created_by_name', 'questions_count',
            'user_attempts', 'user_best_score', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_attempts', 'average_score', 'average_time',
            'created_at', 'updated_at'
        ]
    
    def get_user_attempts(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.attempts.filter(user=request.user).count()
        return 0
    
    def get_user_best_score(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            best_attempt = obj.attempts.filter(
                user=request.user,
                status='completed'
            ).order_by('-score').first()
            return best_attempt.score if best_attempt else 0.0
        return 0.0
    
    def get_questions_count(self, obj):
        # Retornar número de questões que serão geradas
        return obj.max_questions


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer para tentativas de quiz"""
    
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'quiz_title', 'status', 'started_at', 'completed_at',
            'time_spent', 'total_questions', 'correct_answers', 'score',
            'xp_earned', 'coins_earned', 'subject_scores', 'difficulty_breakdown',
            'accuracy_rate'
        ]
        read_only_fields = [
            'started_at', 'completed_at', 'xp_earned', 'coins_earned',
            'subject_scores', 'difficulty_breakdown', 'accuracy_rate'
        ]
    
    def create(self, validated_data):
        # Garantir que o usuário é o da requisição
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class QuestionReportSerializer(serializers.ModelSerializer):
    """Serializer para denúncias de questões"""
    
    question_title = serializers.CharField(source='question.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)
    
    class Meta:
        model = QuestionReport
        fields = [
            'id', 'question', 'question_title', 'user_name', 'report_type',
            'description', 'status', 'reviewed_by', 'reviewed_by_name',
            'resolution_notes', 'resolved_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user_name', 'reviewed_by', 'reviewed_by_name',
            'resolution_notes', 'resolved_at', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        # Garantir que o usuário é o da requisição
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# Serializers para estatísticas e dashboards
class QuestionStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas de questões"""
    
    total_questions = serializers.IntegerField()
    answered_questions = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    accuracy_rate = serializers.FloatField()
    average_time = serializers.FloatField()
    
    # Por disciplina
    subjects_stats = serializers.JSONField()
    
    # Por dificuldade
    difficulty_stats = serializers.JSONField()
    
    # Por banca
    exam_boards_stats = serializers.JSONField()


class QuizStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas de quizzes"""
    
    total_quizzes = serializers.IntegerField()
    completed_quizzes = serializers.IntegerField()
    average_score = serializers.FloatField()
    total_time_spent = serializers.IntegerField()
    xp_earned = serializers.IntegerField()
    coins_earned = serializers.IntegerField()
    
    # Últimas tentativas
    recent_attempts = QuizAttemptSerializer(many=True, read_only=True)


# Serializers simplificados para listagens
class ExamBoardListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de bancas"""
    
    class Meta:
        model = ExamBoard
        fields = ['id', 'name', 'acronym', 'total_questions']


class QuizListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de quizzes"""
    
    exam_board_name = serializers.CharField(source='exam_board.acronym', read_only=True)
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'quiz_type', 'difficulty_level',
            'exam_board_name', 'max_questions', 'time_limit_minutes',
            'is_premium', 'average_score', 'total_attempts'
        ] 