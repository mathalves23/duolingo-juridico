"""
Modelos do sistema de gamificação do Duolingo Jurídico
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

User = get_user_model()


class Achievement(models.Model):
    """Conquistas/Emblemas do sistema"""
    
    ACHIEVEMENT_TYPES = [
        ('streak', 'Streak'),
        ('xp', 'Experiência'),
        ('lessons', 'Lições'),
        ('quiz', 'Quizzes'),
        ('accuracy', 'Precisão'),
        ('speed', 'Velocidade'),
        ('special', 'Especial'),
        ('social', 'Social'),
    ]
    
    RARITY_LEVELS = [
        ('common', 'Comum'),
        ('rare', 'Raro'),
        ('epic', 'Épico'),
        ('legendary', 'Lendário'),
        ('mythic', 'Mítico'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    rarity = models.CharField(max_length=20, choices=RARITY_LEVELS, default='common')
    
    # Critérios para desbloqueio
    requirements = models.JSONField(default=dict)  # Critérios específicos
    
    # Recompensas
    xp_reward = models.PositiveIntegerField(default=0)
    coin_reward = models.PositiveIntegerField(default=0)
    gem_reward = models.PositiveIntegerField(default=0)
    
    # Visual
    icon = models.ImageField(upload_to='achievements/icons/', blank=True, null=True)
    badge_color = models.CharField(max_length=7, default='#FFD700')  # Cor do emblema
    
    # Metadados
    is_active = models.BooleanField(default=True)
    is_secret = models.BooleanField(default=False)  # Conquista secreta
    unlock_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Conquista'
        verbose_name_plural = 'Conquistas'
        ordering = ['achievement_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"
    
    def check_requirements(self, user):
        """Verifica se o usuário atende aos requisitos"""
        reqs = self.requirements
        
        if self.achievement_type == 'streak':
            return user.current_streak >= reqs.get('days', 1)
        
        elif self.achievement_type == 'xp':
            return user.total_xp >= reqs.get('total_xp', 100)
        
        elif self.achievement_type == 'lessons':
            completed_lessons = user.user_lessons.filter(completed=True).count()
            return completed_lessons >= reqs.get('total_lessons', 10)
        
        elif self.achievement_type == 'quiz':
            completed_quizzes = user.quiz_attempts.filter(status='completed').count()
            return completed_quizzes >= reqs.get('total_quizzes', 5)
        
        elif self.achievement_type == 'accuracy':
            return user.accuracy_rate >= reqs.get('min_accuracy', 80)
        
        # Adicionar mais verificações conforme necessário
        return False


class UserAchievement(models.Model):
    """Conquistas desbloqueadas pelos usuários"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='unlocked_by')
    
    unlocked_at = models.DateTimeField(auto_now_add=True)
    progress_when_unlocked = models.JSONField(default=dict)  # Progresso quando desbloqueou
    
    # Recompensas recebidas
    xp_received = models.PositiveIntegerField(default=0)
    coins_received = models.PositiveIntegerField(default=0)
    gems_received = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Conquista do Usuário'
        verbose_name_plural = 'Conquistas dos Usuários'
        unique_together = ['user', 'achievement']
        ordering = ['-unlocked_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


class Leaderboard(models.Model):
    """Rankings/Tabelas de classificação"""
    
    LEADERBOARD_TYPES = [
        ('global_xp', 'XP Global'),
        ('weekly_xp', 'XP Semanal'),
        ('monthly_xp', 'XP Mensal'),
        ('streak', 'Streak Atual'),
        ('lessons', 'Lições Completadas'),
        ('quiz_accuracy', 'Precisão em Quizzes'),
        ('subject_specific', 'Específico por Disciplina'),
    ]
    
    PERIODS = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('yearly', 'Anual'),
        ('all_time', 'Todos os Tempos'),
    ]
    
    name = models.CharField(max_length=100)
    leaderboard_type = models.CharField(max_length=20, choices=LEADERBOARD_TYPES)
    period = models.CharField(max_length=20, choices=PERIODS)
    
    # Filtros específicos
    subject_filter = models.ForeignKey(
        'courses.Subject', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True
    )
    
    # Configurações
    max_entries = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    
    # Período atual
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    
    # Última atualização
    last_updated = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Ranking'
        verbose_name_plural = 'Rankings'
        ordering = ['leaderboard_type', 'period']
    
    def __str__(self):
        return f"{self.name} ({self.get_period_display()})"
    
    def update_rankings(self):
        """Atualiza o ranking com dados atuais"""
        # Limpar entradas antigas
        self.entries.all().delete()
        
        if self.leaderboard_type == 'global_xp':
            users = User.objects.order_by('-total_xp')[:self.max_entries]
            for position, user in enumerate(users, 1):
                LeaderboardEntry.objects.create(
                    leaderboard=self,
                    user=user,
                    position=position,
                    score=user.total_xp,
                    period_start=self.current_period_start,
                    period_end=self.current_period_end
                )
        
        elif self.leaderboard_type == 'weekly_xp':
            # Implementar lógica para XP semanal
            pass
        
        # Adicionar outras lógicas conforme necessário
        self.last_updated = timezone.now()
        self.save()


class LeaderboardEntry(models.Model):
    """Entradas individuais nos rankings"""
    
    leaderboard = models.ForeignKey(
        Leaderboard, 
        on_delete=models.CASCADE, 
        related_name='entries'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaderboard_entries')
    
    position = models.PositiveIntegerField()
    score = models.FloatField()
    previous_position = models.PositiveIntegerField(blank=True, null=True)
    
    # Período da entrada
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Entrada do Ranking'
        verbose_name_plural = 'Entradas dos Rankings'
        ordering = ['leaderboard', 'position']
        unique_together = ['leaderboard', 'user', 'period_start']
    
    def __str__(self):
        return f"{self.leaderboard.name} - #{self.position} {self.user.username}"
    
    @property
    def position_change(self):
        """Mudança de posição desde o período anterior"""
        if self.previous_position:
            return self.previous_position - self.position
        return 0


class StoreItem(models.Model):
    """Itens da loja virtual"""
    
    ITEM_TYPES = [
        ('cosmetic', 'Cosmético'),
        ('avatar', 'Avatar'),
        ('theme', 'Tema'),
        ('boost', 'Impulso'),
        ('premium', 'Premium'),
        ('lives', 'Vidas'),
        ('streak_freeze', 'Congelamento de Streak'),
        ('double_xp', 'XP Duplo'),
    ]
    
    CURRENCY_TYPES = [
        ('coins', 'Moedas'),
        ('gems', 'Gemas'),
        ('real_money', 'Dinheiro Real'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    
    # Preços
    coin_price = models.PositiveIntegerField(blank=True, null=True)
    gem_price = models.PositiveIntegerField(blank=True, null=True)
    real_price = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        blank=True, 
        null=True
    )
    
    # Visual e metadados
    image = models.ImageField(upload_to='store/items/', blank=True, null=True)
    preview_image = models.ImageField(upload_to='store/previews/', blank=True, null=True)
    
    # Configurações do item
    item_data = models.JSONField(default=dict)  # Dados específicos do item
    duration_hours = models.PositiveIntegerField(blank=True, null=True)  # Para itens temporários
    
    # Disponibilidade
    is_active = models.BooleanField(default=True)
    is_limited = models.BooleanField(default=False)
    stock_quantity = models.PositiveIntegerField(blank=True, null=True)
    
    # Datas especiais
    available_from = models.DateTimeField(blank=True, null=True)
    available_until = models.DateTimeField(blank=True, null=True)
    
    # Estatísticas
    purchase_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Item da Loja'
        verbose_name_plural = 'Itens da Loja'
        ordering = ['item_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_item_type_display()})"
    
    @property
    def is_available(self):
        """Verifica se o item está disponível para compra"""
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if self.available_from and now < self.available_from:
            return False
        
        if self.available_until and now > self.available_until:
            return False
        
        if self.is_limited and self.stock_quantity is not None:
            return self.stock_quantity > 0
        
        return True


class UserPurchase(models.Model):
    """Compras realizadas pelos usuários"""
    
    PAYMENT_METHODS = [
        ('coins', 'Moedas'),
        ('gems', 'Gemas'),
        ('credit_card', 'Cartão de Crédito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
        ('refunded', 'Estornado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    item = models.ForeignKey(StoreItem, on_delete=models.CASCADE, related_name='purchases')
    
    # Detalhes da compra
    quantity = models.PositiveIntegerField(default=1)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    # Valores
    coins_spent = models.PositiveIntegerField(default=0)
    gems_spent = models.PositiveIntegerField(default=0)
    real_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Dados do pagamento externo
    external_transaction_id = models.CharField(max_length=200, blank=True)
    payment_data = models.JSONField(default=dict)
    
    # Timestamps
    purchased_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-purchased_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.item.name} ({self.status})"
    
    def complete_purchase(self):
        """Finaliza a compra e aplica os efeitos"""
        if self.status != 'pending':
            return False
        
        # Verificar se usuário tem recursos suficientes
        if self.payment_method == 'coins':
            if self.user.coins < self.coins_spent:
                self.status = 'failed'
                self.save()
                return False
            self.user.coins -= self.coins_spent
        
        elif self.payment_method == 'gems':
            if self.user.gems < self.gems_spent:
                self.status = 'failed'
                self.save()
                return False
            self.user.gems -= self.gems_spent
        
        # Aplicar efeitos do item
        self._apply_item_effects()
        
        # Finalizar compra
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        
        self.user.save()
        return True
    
    def _apply_item_effects(self):
        """Aplica os efeitos do item comprado"""
        if self.item.item_type == 'streak_freeze':
            # Implementar congelamento de streak
            pass
        elif self.item.item_type == 'double_xp':
            # Implementar XP duplo
            UserBoost.objects.create(
                user=self.user,
                boost_type='double_xp',
                duration_hours=self.item.duration_hours or 24,
                purchase=self
            )
        elif self.item.item_type == 'lives':
            # Adicionar vidas
            lives_to_add = self.item.item_data.get('lives', 5)
            # Implementar sistema de vidas se necessário
        
        # Incrementar contador de compras do item
        self.item.purchase_count += 1
        self.item.save()


class UserBoost(models.Model):
    """Impulsos ativos dos usuários"""
    
    BOOST_TYPES = [
        ('double_xp', 'XP Duplo'),
        ('double_coins', 'Moedas Duplas'),
        ('streak_freeze', 'Congelamento de Streak'),
        ('unlimited_lives', 'Vidas Infinitas'),
        ('skip_cooldown', 'Pular Cooldown'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='active_boosts')
    boost_type = models.CharField(max_length=20, choices=BOOST_TYPES)
    
    # Duração
    activated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    duration_hours = models.PositiveIntegerField()
    
    # Origem
    purchase = models.ForeignKey(
        UserPurchase, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Impulso do Usuário'
        verbose_name_plural = 'Impulsos dos Usuários'
        ordering = ['-activated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_boost_type_display()}"
    
    @property
    def is_expired(self):
        """Verifica se o impulso expirou"""
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = self.activated_at + timezone.timedelta(hours=self.duration_hours)
        super().save(*args, **kwargs)


class DailyChallenge(models.Model):
    """Desafios diários"""
    
    CHALLENGE_TYPES = [
        ('questions', 'Responder Questões'),
        ('accuracy', 'Taxa de Acerto'),
        ('speed', 'Velocidade'),
        ('streak', 'Sequência'),
        ('study_time', 'Tempo de Estudo'),
        ('subject_focus', 'Foco em Matéria'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('easy', 'Fácil'),
        ('medium', 'Médio'),
        ('hard', 'Difícil'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES, verbose_name="Tipo")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS, verbose_name="Dificuldade")
    
    # Data do desafio
    date = models.DateField(verbose_name="Data")
    
    # Configurações do desafio
    target_value = models.PositiveIntegerField(verbose_name="Valor alvo")
    conditions = models.JSONField(
        default=dict,
        help_text="Condições específicas do desafio",
        verbose_name="Condições"
    )
    
    # Recompensas
    xp_reward = models.PositiveIntegerField(default=50, verbose_name="XP de recompensa")
    gems_reward = models.PositiveIntegerField(default=5, verbose_name="Gemas de recompensa")
    additional_rewards = models.JSONField(
        default=dict,
        help_text="Recompensas adicionais",
        verbose_name="Recompensas adicionais"
    )
    
    # Estatísticas
    total_participants = models.PositiveIntegerField(default=0, verbose_name="Total de participantes")
    completion_rate = models.FloatField(default=0.0, verbose_name="Taxa de conclusão")
    
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Desafio Diário"
        verbose_name_plural = "Desafios Diários"
        unique_together = ['date', 'challenge_type']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.title} - {self.date}"
    
    @property
    def is_today(self):
        return self.date == timezone.now().date()


class DailyChallengeCompletion(models.Model):
    """Conclusão de desafios diários"""
    
    STATUS_CHOICES = [
        ('in_progress', 'Em Progresso'),
        ('completed', 'Concluído'),
        ('failed', 'Falhado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE, related_name='completions', verbose_name="Desafio")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='challenge_completions', verbose_name="Usuário")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress', verbose_name="Status")
    
    # Progresso
    current_progress = models.PositiveIntegerField(default=0, verbose_name="Progresso atual")
    progress_data = models.JSONField(
        default=dict,
        help_text="Dados detalhados do progresso",
        verbose_name="Dados do progresso"
    )
    
    # Recompensas
    rewards_claimed = models.BooleanField(default=False, verbose_name="Recompensas coletadas")
    
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Iniciado em")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Concluído em")
    
    class Meta:
        verbose_name = "Conclusão de Desafio Diário"
        verbose_name_plural = "Conclusões de Desafios Diários"
        unique_together = ['challenge', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.challenge.title}"
    
    @property
    def completion_percentage(self):
        if self.challenge.target_value > 0:
            return min(100, (self.current_progress / self.challenge.target_value) * 100)
        return 0
    
    def check_completion(self):
        """Verifica se o desafio foi concluído"""
        if self.current_progress >= self.challenge.target_value:
            self.status = 'completed'
            if not self.completed_at:
                self.completed_at = timezone.now()
            self.save()
            return True
        return False


class Clan(models.Model):
    """Sistema de clãs/grupos"""
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('disbanded', 'Dissolvido'),
    ]
    
    JOINING_POLICY = [
        ('open', 'Aberto'),
        ('invite_only', 'Apenas Convite'),
        ('application', 'Por Aplicação'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    tag = models.CharField(max_length=10, unique=True, verbose_name="Tag")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_clans', verbose_name="Líder")
    members = models.ManyToManyField(User, through='ClanMembership', related_name='clans', verbose_name="Membros")
    
    # Configurações
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    joining_policy = models.CharField(max_length=20, choices=JOINING_POLICY, default='open', verbose_name="Política de entrada")
    max_members = models.PositiveIntegerField(default=50, verbose_name="Máximo de membros")
    
    # Pontuação do clã
    total_points = models.PositiveIntegerField(default=0, verbose_name="Pontos totais")
    weekly_points = models.PositiveIntegerField(default=0, verbose_name="Pontos semanais")
    
    # Estatísticas
    level = models.PositiveIntegerField(default=1, verbose_name="Nível")
    total_study_time = models.PositiveIntegerField(default=0, verbose_name="Tempo total de estudo")
    total_questions_answered = models.PositiveIntegerField(default=0, verbose_name="Total de questões respondidas")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Clã"
        verbose_name_plural = "Clãs"
        ordering = ['-total_points']
    
    def __str__(self):
        return f"[{self.tag}] {self.name}"
    
    @property
    def member_count(self):
        return self.members.count()
    
    @property
    def is_full(self):
        return self.member_count >= self.max_members


class ClanMembership(models.Model):
    """Participação em clãs"""
    
    ROLE_CHOICES = [
        ('member', 'Membro'),
        ('officer', 'Oficial'),
        ('co_leader', 'Vice-Líder'),
        ('leader', 'Líder'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('kicked', 'Expulso'),
        ('left', 'Saiu'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, verbose_name="Clã")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name="Papel")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    
    # Contribuições
    points_contributed = models.PositiveIntegerField(default=0, verbose_name="Pontos contribuídos")
    weekly_contribution = models.PositiveIntegerField(default=0, verbose_name="Contribuição semanal")
    
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Entrou em")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Última atividade")
    
    class Meta:
        verbose_name = "Participação em Clã"
        verbose_name_plural = "Participações em Clãs"
        unique_together = ['clan', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.clan.name}"


# Expandindo modelos existentes
class Achievement(models.Model):
    """Conquistas expandidas"""
    
    ACHIEVEMENT_CATEGORIES = [
        ('study', 'Estudo'),
        ('accuracy', 'Precisão'),
        ('speed', 'Velocidade'),
        ('consistency', 'Consistência'),
        ('social', 'Social'),
        ('competition', 'Competição'),
        ('special', 'Especial'),
        ('milestone', 'Marco'),
    ]
    
    RARITY_LEVELS = [
        ('common', 'Comum'),
        ('uncommon', 'Incomum'),
        ('rare', 'Raro'),
        ('epic', 'Épico'),
        ('legendary', 'Lendário'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    icon = models.CharField(max_length=100, verbose_name="Ícone")
    
    category = models.CharField(max_length=20, choices=ACHIEVEMENT_CATEGORIES, verbose_name="Categoria")
    rarity = models.CharField(max_length=20, choices=RARITY_LEVELS, default='common', verbose_name="Raridade")
    
    # Condições para conquistar
    conditions = models.JSONField(
        default=dict,
        help_text="Condições necessárias para conquistar",
        verbose_name="Condições"
    )
    
    # Recompensas
    xp_reward = models.PositiveIntegerField(default=100, verbose_name="XP de recompensa")
    gems_reward = models.PositiveIntegerField(default=10, verbose_name="Gemas de recompensa")
    points_reward = models.PositiveIntegerField(default=50, verbose_name="Pontos de recompensa")
    title_reward = models.CharField(max_length=100, blank=True, verbose_name="Título desbloqueado")
    
    # Configurações
    is_hidden = models.BooleanField(default=False, verbose_name="Oculto")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Ordem de exibição")
    
    # Estatísticas
    total_earned = models.PositiveIntegerField(default=0, verbose_name="Total de usuários que conquistaram")
    first_earned_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Primeiro a conquistar")
    first_earned_at = models.DateTimeField(null=True, blank=True, verbose_name="Primeira conquista em")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Conquista"
        verbose_name_plural = "Conquistas"
        ordering = ['category', 'sort_order']
    
    def __str__(self):
        return self.title


class UserAchievement(models.Model):
    """Conquistas dos usuários"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_achievements', verbose_name="Usuário")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, verbose_name="Conquista")
    
    # Progresso (para conquistas progressivas)
    progress = models.PositiveIntegerField(default=0, verbose_name="Progresso")
    is_completed = models.BooleanField(default=False, verbose_name="Concluído")
    
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name="Conquistado em")
    
    class Meta:
        verbose_name = "Conquista do Usuário"
        verbose_name_plural = "Conquistas dos Usuários"
        unique_together = ['user', 'achievement']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.achievement.title}"
