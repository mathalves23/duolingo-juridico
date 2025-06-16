"""
Modelos para funcionalidades sociais do Duolingo Jurídico
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta

User = get_user_model()


class StudyGroup(models.Model):
    """Grupos de estudo"""
    
    PRIVACY_CHOICES = [
        ('public', 'Público'),
        ('private', 'Privado'),
        ('invite_only', 'Apenas convidados'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('paused', 'Pausado'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups', verbose_name="Criador")
    members = models.ManyToManyField(User, through='StudyGroupMembership', related_name='study_groups', verbose_name="Membros")
    
    # Configurações do grupo
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public', verbose_name="Privacidade")
    max_members = models.PositiveIntegerField(default=50, validators=[MinValueValidator(2), MaxValueValidator(500)], verbose_name="Máximo de membros")
    subjects = models.ManyToManyField('core.Subject', blank=True, verbose_name="Matérias de foco")
    target_exam = models.CharField(max_length=200, blank=True, verbose_name="Concurso alvo")
    
    # Status e datas
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    start_date = models.DateField(null=True, blank=True, verbose_name="Data de início")
    end_date = models.DateField(null=True, blank=True, verbose_name="Data de término")
    
    # Configurações de estudo
    study_schedule = models.JSONField(
        default=dict,
        help_text="Cronograma de estudos do grupo",
        verbose_name="Cronograma"
    )
    weekly_goals = models.JSONField(
        default=dict,
        help_text="Metas semanais do grupo",
        verbose_name="Metas semanais"
    )
    
    # Estatísticas
    total_study_time = models.PositiveIntegerField(default=0, verbose_name="Tempo total de estudo (minutos)")
    total_questions_answered = models.PositiveIntegerField(default=0, verbose_name="Total de questões respondidas")
    group_accuracy_rate = models.FloatField(default=0.0, verbose_name="Taxa de acerto do grupo")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Grupo de Estudo"
        verbose_name_plural = "Grupos de Estudo"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def member_count(self):
        return self.members.count()
    
    @property
    def is_full(self):
        return self.member_count >= self.max_members
    
    def can_join(self, user):
        """Verifica se um usuário pode se juntar ao grupo"""
        if self.is_full:
            return False
        if user in self.members.all():
            return False
        if self.privacy == 'private':
            return False
        if self.privacy == 'invite_only':
            return StudyGroupInvitation.objects.filter(
                group=self, 
                invitee=user, 
                status='pending'
            ).exists()
        return True


class StudyGroupMembership(models.Model):
    """Participação em grupos de estudo"""
    
    ROLE_CHOICES = [
        ('member', 'Membro'),
        ('moderator', 'Moderador'),
        ('admin', 'Administrador'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('banned', 'Banido'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, verbose_name="Grupo")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name="Papel")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    
    # Estatísticas do membro
    personal_study_time = models.PositiveIntegerField(default=0, verbose_name="Tempo pessoal de estudo (minutos)")
    questions_answered = models.PositiveIntegerField(default=0, verbose_name="Questões respondidas")
    accuracy_rate = models.FloatField(default=0.0, verbose_name="Taxa de acerto")
    contribution_score = models.PositiveIntegerField(default=0, verbose_name="Pontuação de contribuição")
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Entrou em")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Última atividade")
    
    class Meta:
        verbose_name = "Participação em Grupo"
        verbose_name_plural = "Participações em Grupos"
        unique_together = ['group', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.group.name}"


class StudyGroupInvitation(models.Model):
    """Convites para grupos de estudo"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('accepted', 'Aceito'),
        ('declined', 'Recusado'),
        ('expired', 'Expirado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, verbose_name="Grupo")
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations', verbose_name="Quem convidou")
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations', verbose_name="Convidado")
    
    message = models.TextField(blank=True, verbose_name="Mensagem do convite")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    expires_at = models.DateTimeField(verbose_name="Expira em")
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name="Respondido em")
    
    class Meta:
        verbose_name = "Convite para Grupo"
        verbose_name_plural = "Convites para Grupos"
        unique_together = ['group', 'invitee']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def accept(self):
        """Aceita o convite"""
        if self.status == 'pending' and not self.is_expired:
            self.status = 'accepted'
            self.responded_at = timezone.now()
            self.save()
            
            # Adiciona o usuário ao grupo
            StudyGroupMembership.objects.get_or_create(
                group=self.group,
                user=self.invitee,
                defaults={'role': 'member'}
            )
            return True
        return False
    
    def decline(self):
        """Recusa o convite"""
        if self.status == 'pending':
            self.status = 'declined'
            self.responded_at = timezone.now()
            self.save()
            return True
        return False


class DiscussionForum(models.Model):
    """Fóruns de discussão"""
    
    CATEGORY_CHOICES = [
        ('general', 'Geral'),
        ('subject_discussion', 'Discussão de Matérias'),
        ('exam_preparation', 'Preparação para Concursos'),
        ('question_discussion', 'Discussão de Questões'),
        ('study_tips', 'Dicas de Estudo'),
        ('legal_updates', 'Atualizações Jurídicas'),
        ('career_advice', 'Orientação de Carreira'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, verbose_name="Categoria")
    
    moderators = models.ManyToManyField(User, blank=True, related_name='moderated_forums', verbose_name="Moderadores")
    
    # Configurações
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    requires_approval = models.BooleanField(default=False, verbose_name="Requer aprovação")
    allow_anonymous_posts = models.BooleanField(default=False, verbose_name="Permite posts anônimos")
    
    # Estatísticas
    total_topics = models.PositiveIntegerField(default=0, verbose_name="Total de tópicos")
    total_posts = models.PositiveIntegerField(default=0, verbose_name="Total de posts")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Fórum de Discussão"
        verbose_name_plural = "Fóruns de Discussão"
        ordering = ['category', 'title']
    
    def __str__(self):
        return self.title


class ForumTopic(models.Model):
    """Tópicos do fórum"""
    
    STATUS_CHOICES = [
        ('open', 'Aberto'),
        ('closed', 'Fechado'),
        ('pinned', 'Fixado'),
        ('locked', 'Bloqueado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    forum = models.ForeignKey(DiscussionForum, on_delete=models.CASCADE, related_name='topics', verbose_name="Fórum")
    title = models.CharField(max_length=200, verbose_name="Título")
    content = models.TextField(verbose_name="Conteúdo")
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics', verbose_name="Autor")
    is_anonymous = models.BooleanField(default=False, verbose_name="Anônimo")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="Status")
    is_approved = models.BooleanField(default=True, verbose_name="Aprovado")
    
    # Relacionamentos
    related_question = models.ForeignKey('core.Question', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Questão relacionada")
    tags = models.ManyToManyField('core.Tag', blank=True, verbose_name="Tags")
    
    # Estatísticas
    view_count = models.PositiveIntegerField(default=0, verbose_name="Visualizações")
    reply_count = models.PositiveIntegerField(default=0, verbose_name="Respostas")
    like_count = models.PositiveIntegerField(default=0, verbose_name="Curtidas")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    last_reply_at = models.DateTimeField(null=True, blank=True, verbose_name="Última resposta em")
    
    class Meta:
        verbose_name = "Tópico do Fórum"
        verbose_name_plural = "Tópicos do Fórum"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class ForumPost(models.Model):
    """Posts/respostas do fórum"""
    
    STATUS_CHOICES = [
        ('published', 'Publicado'),
        ('pending', 'Pendente'),
        ('hidden', 'Oculto'),
        ('flagged', 'Sinalizado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='posts', verbose_name="Tópico")
    content = models.TextField(verbose_name="Conteúdo")
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts', verbose_name="Autor")
    is_anonymous = models.BooleanField(default=False, verbose_name="Anônimo")
    
    # Hierarquia de respostas
    parent_post = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name="Post pai")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published', verbose_name="Status")
    is_approved = models.BooleanField(default=True, verbose_name="Aprovado")
    is_solution = models.BooleanField(default=False, verbose_name="É solução")
    
    # Estatísticas
    like_count = models.PositiveIntegerField(default=0, verbose_name="Curtidas")
    dislike_count = models.PositiveIntegerField(default=0, verbose_name="Descurtidas")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Post do Fórum"
        verbose_name_plural = "Posts do Fórum"
        ordering = ['created_at']
    
    def __str__(self):
        return f"Post de {self.author.get_full_name()} em {self.topic.title}"


class UserFriendship(models.Model):
    """Sistema de amizade entre usuários"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('accepted', 'Aceito'),
        ('blocked', 'Bloqueado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests', verbose_name="Solicitante")
    addressee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests', verbose_name="Destinatário")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Amizade"
        verbose_name_plural = "Amizades"
        unique_together = ['requester', 'addressee']
    
    def __str__(self):
        return f"{self.requester.get_full_name()} -> {self.addressee.get_full_name()}"
    
    def accept(self):
        """Aceita a solicitação de amizade"""
        if self.status == 'pending':
            self.status = 'accepted'
            self.save()
            return True
        return False
    
    def block(self):
        """Bloqueia o usuário"""
        self.status = 'blocked'
        self.save()


class StudySession(models.Model):
    """Sessões de estudo individuais ou em grupo"""
    
    SESSION_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('group', 'Em Grupo'),
        ('collaborative', 'Colaborativa'),
    ]
    
    STATUS_CHOICES = [
        ('planned', 'Planejada'),
        ('ongoing', 'Em Andamento'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, verbose_name="Tipo")
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_sessions', verbose_name="Organizador")
    participants = models.ManyToManyField(User, through='StudySessionParticipation', related_name='study_sessions', verbose_name="Participantes")
    
    # Configurações da sessão
    study_group = models.ForeignKey(StudyGroup, null=True, blank=True, on_delete=models.CASCADE, related_name='sessions', verbose_name="Grupo de estudo")
    subjects = models.ManyToManyField('core.Subject', verbose_name="Matérias")
    difficulty_level = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Nível de dificuldade")
    
    # Datas e horários
    scheduled_start = models.DateTimeField(verbose_name="Início programado")
    scheduled_end = models.DateTimeField(verbose_name="Fim programado")
    actual_start = models.DateTimeField(null=True, blank=True, verbose_name="Início real")
    actual_end = models.DateTimeField(null=True, blank=True, verbose_name="Fim real")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned', verbose_name="Status")
    
    # Configurações de acesso
    is_public = models.BooleanField(default=False, verbose_name="Público")
    max_participants = models.PositiveIntegerField(default=10, verbose_name="Máximo de participantes")
    requires_approval = models.BooleanField(default=False, verbose_name="Requer aprovação")
    
    # Estatísticas
    total_questions = models.PositiveIntegerField(default=0, verbose_name="Total de questões")
    average_accuracy = models.FloatField(default=0.0, verbose_name="Precisão média")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Sessão de Estudo"
        verbose_name_plural = "Sessões de Estudo"
        ordering = ['-scheduled_start']
    
    def __str__(self):
        return self.title
    
    @property
    def duration_planned(self):
        """Duração planejada em minutos"""
        return (self.scheduled_end - self.scheduled_start).total_seconds() / 60
    
    @property
    def duration_actual(self):
        """Duração real em minutos"""
        if self.actual_start and self.actual_end:
            return (self.actual_end - self.actual_start).total_seconds() / 60
        return 0


class StudySessionParticipation(models.Model):
    """Participação em sessões de estudo"""
    
    STATUS_CHOICES = [
        ('registered', 'Registrado'),
        ('confirmed', 'Confirmado'),
        ('attended', 'Participou'),
        ('missed', 'Faltou'),
        ('cancelled', 'Cancelou'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, verbose_name="Sessão")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered', verbose_name="Status")
    
    # Estatísticas individuais
    questions_answered = models.PositiveIntegerField(default=0, verbose_name="Questões respondidas")
    correct_answers = models.PositiveIntegerField(default=0, verbose_name="Respostas corretas")
    time_spent = models.PositiveIntegerField(default=0, verbose_name="Tempo gasto (minutos)")
    participation_score = models.PositiveIntegerField(default=0, verbose_name="Pontuação de participação")
    
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Entrou em")
    left_at = models.DateTimeField(null=True, blank=True, verbose_name="Saiu em")
    
    class Meta:
        verbose_name = "Participação em Sessão"
        verbose_name_plural = "Participações em Sessões"
        unique_together = ['session', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.session.title}"
    
    @property
    def accuracy_rate(self):
        """Taxa de acerto"""
        if self.questions_answered > 0:
            return (self.correct_answers / self.questions_answered) * 100
        return 0 