"""
Modelos para integrações externas do Duolingo Jurídico
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import URLValidator
from datetime import timedelta
import json

User = get_user_model()


class ExternalProvider(models.Model):
    """Provedores de conteúdo externos"""
    
    PROVIDER_TYPES = [
        ('question_bank', 'Banco de Questões'),
        ('legal_news', 'Notícias Jurídicas'),
        ('exam_board', 'Banca de Concurso'),
        ('legal_database', 'Base Legal'),
        ('study_material', 'Material de Estudo'),
        ('video_platform', 'Plataforma de Vídeos'),
        ('social_media', 'Mídia Social'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('maintenance', 'Manutenção'),
        ('deprecated', 'Descontinuado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    provider_type = models.CharField(max_length=30, choices=PROVIDER_TYPES, verbose_name="Tipo")
    
    # Configurações de conexão
    base_url = models.URLField(verbose_name="URL Base")
    api_version = models.CharField(max_length=10, default='v1', verbose_name="Versão da API")
    authentication_type = models.CharField(
        max_length=20,
        choices=[
            ('none', 'Nenhuma'),
            ('api_key', 'API Key'),
            ('oauth2', 'OAuth 2.0'),
            ('basic_auth', 'Autenticação Básica'),
            ('jwt', 'JWT Token'),
        ],
        default='api_key',
        verbose_name="Tipo de Autenticação"
    )
    
    # Credenciais (armazenadas de forma segura)
    api_key = models.CharField(max_length=500, blank=True, verbose_name="API Key")
    api_secret = models.CharField(max_length=500, blank=True, verbose_name="API Secret")
    oauth_config = models.JSONField(
        default=dict,
        help_text="Configurações OAuth",
        verbose_name="Configuração OAuth"
    )
    
    # Configurações de sincronização
    sync_frequency = models.PositiveIntegerField(
        default=60,
        help_text="Frequência de sincronização em minutos",
        verbose_name="Frequência de Sincronização"
    )
    last_sync = models.DateTimeField(null=True, blank=True, verbose_name="Última Sincronização")
    next_sync = models.DateTimeField(null=True, blank=True, verbose_name="Próxima Sincronização")
    
    # Status e configurações
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    is_premium = models.BooleanField(default=False, verbose_name="Premium")
    rate_limit_per_hour = models.PositiveIntegerField(default=1000, verbose_name="Limite de Requisições/Hora")
    
    # Mapeamentos de dados
    field_mappings = models.JSONField(
        default=dict,
        help_text="Mapeamento entre campos externos e internos",
        verbose_name="Mapeamento de Campos"
    )
    
    # Estatísticas
    total_requests = models.PositiveIntegerField(default=0, verbose_name="Total de Requisições")
    successful_requests = models.PositiveIntegerField(default=0, verbose_name="Requisições Bem-sucedidas")
    failed_requests = models.PositiveIntegerField(default=0, verbose_name="Requisições Falhadas")
    last_error = models.TextField(blank=True, verbose_name="Último Erro")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Provedor Externo"
        verbose_name_plural = "Provedores Externos"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def success_rate(self):
        if self.total_requests > 0:
            return (self.successful_requests / self.total_requests) * 100
        return 0
    
    def is_sync_due(self):
        """Verifica se é hora de sincronizar"""
        if not self.next_sync:
            return True
        return timezone.now() >= self.next_sync
    
    def update_next_sync(self):
        """Atualiza a próxima sincronização"""
        self.next_sync = timezone.now() + timedelta(minutes=self.sync_frequency)
        self.save(update_fields=['next_sync'])


class DataSync(models.Model):
    """Registros de sincronização de dados"""
    
    SYNC_TYPES = [
        ('full', 'Completa'),
        ('incremental', 'Incremental'),
        ('manual', 'Manual'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('running', 'Executando'),
        ('completed', 'Concluída'),
        ('failed', 'Falhada'),
        ('cancelled', 'Cancelada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(ExternalProvider, on_delete=models.CASCADE, related_name='sync_logs', verbose_name="Provedor")
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPES, verbose_name="Tipo")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    
    # Configurações da sincronização
    filters = models.JSONField(
        default=dict,
        help_text="Filtros aplicados na sincronização",
        verbose_name="Filtros"
    )
    
    # Resultados
    items_processed = models.PositiveIntegerField(default=0, verbose_name="Itens Processados")
    items_created = models.PositiveIntegerField(default=0, verbose_name="Itens Criados")
    items_updated = models.PositiveIntegerField(default=0, verbose_name="Itens Atualizados")
    items_skipped = models.PositiveIntegerField(default=0, verbose_name="Itens Ignorados")
    items_failed = models.PositiveIntegerField(default=0, verbose_name="Itens com Falha")
    
    # Logs e erros
    log_messages = models.JSONField(
        default=list,
        help_text="Mensagens de log da sincronização",
        verbose_name="Mensagens de Log"
    )
    error_details = models.TextField(blank=True, verbose_name="Detalhes do Erro")
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Iniciado em")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Concluído em")
    duration_seconds = models.PositiveIntegerField(null=True, blank=True, verbose_name="Duração (segundos)")
    
    class Meta:
        verbose_name = "Sincronização de Dados"
        verbose_name_plural = "Sincronizações de Dados"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.provider.name} - {self.sync_type} - {self.status}"
    
    def mark_completed(self):
        """Marca a sincronização como concluída"""
        if self.status == 'running':
            self.status = 'completed'
            self.completed_at = timezone.now()
            if self.started_at:
                self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
            self.save()


class ExternalContent(models.Model):
    """Conteúdo importado de fontes externas"""
    
    CONTENT_TYPES = [
        ('question', 'Questão'),
        ('article', 'Artigo'),
        ('news', 'Notícia'),
        ('video', 'Vídeo'),
        ('document', 'Documento'),
        ('case_study', 'Caso de Estudo'),
    ]
    
    STATUS_CHOICES = [
        ('imported', 'Importado'),
        ('processed', 'Processado'),
        ('published', 'Publicado'),
        ('rejected', 'Rejeitado'),
        ('outdated', 'Desatualizado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(ExternalProvider, on_delete=models.CASCADE, related_name='content', verbose_name="Provedor")
    
    # Identificação externa
    external_id = models.CharField(max_length=200, verbose_name="ID Externo")
    external_url = models.URLField(blank=True, verbose_name="URL Externa")
    
    # Conteúdo
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, verbose_name="Tipo de Conteúdo")
    title = models.CharField(max_length=500, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descrição")
    content_data = models.JSONField(
        default=dict,
        help_text="Dados completos do conteúdo",
        verbose_name="Dados do Conteúdo"
    )
    
    # Status e processamento
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='imported', verbose_name="Status")
    quality_score = models.FloatField(null=True, blank=True, verbose_name="Pontuação de Qualidade")
    relevance_score = models.FloatField(null=True, blank=True, verbose_name="Pontuação de Relevância")
    
    # Relacionamentos internos
    internal_question = models.ForeignKey('core.Question', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Questão Interna")
    internal_article = models.ForeignKey('core.Article', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Artigo Interno")
    
    # Metadados
    metadata = models.JSONField(
        default=dict,
        help_text="Metadados adicionais",
        verbose_name="Metadados"
    )
    tags = models.JSONField(
        default=list,
        help_text="Tags do conteúdo",
        verbose_name="Tags"
    )
    subjects = models.ManyToManyField('core.Subject', blank=True, verbose_name="Matérias")
    
    # Timestamps
    external_created_at = models.DateTimeField(null=True, blank=True, verbose_name="Criado externamente em")
    external_updated_at = models.DateTimeField(null=True, blank=True, verbose_name="Atualizado externamente em")
    imported_at = models.DateTimeField(auto_now_add=True, verbose_name="Importado em")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Processado em")
    
    class Meta:
        verbose_name = "Conteúdo Externo"
        verbose_name_plural = "Conteúdos Externos"
        unique_together = ['provider', 'external_id']
        ordering = ['-imported_at']
    
    def __str__(self):
        return f"{self.provider.name} - {self.title}"


class APIUsageLog(models.Model):
    """Log de uso de APIs externas"""
    
    REQUEST_METHODS = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(ExternalProvider, on_delete=models.CASCADE, related_name='api_logs', verbose_name="Provedor")
    
    # Detalhes da requisição
    endpoint = models.CharField(max_length=500, verbose_name="Endpoint")
    method = models.CharField(max_length=10, choices=REQUEST_METHODS, verbose_name="Método")
    request_headers = models.JSONField(default=dict, verbose_name="Cabeçalhos da Requisição")
    request_body = models.TextField(blank=True, verbose_name="Corpo da Requisição")
    
    # Resposta
    status_code = models.PositiveIntegerField(verbose_name="Código de Status")
    response_headers = models.JSONField(default=dict, verbose_name="Cabeçalhos da Resposta")
    response_body = models.TextField(blank=True, verbose_name="Corpo da Resposta")
    
    # Métricas
    response_time_ms = models.PositiveIntegerField(verbose_name="Tempo de Resposta (ms)")
    request_size_bytes = models.PositiveIntegerField(default=0, verbose_name="Tamanho da Requisição (bytes)")
    response_size_bytes = models.PositiveIntegerField(default=0, verbose_name="Tamanho da Resposta (bytes)")
    
    # Contexto
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Usuário")
    operation = models.CharField(max_length=100, blank=True, verbose_name="Operação")
    
    # Erro (se houver)
    error_message = models.TextField(blank=True, verbose_name="Mensagem de Erro")
    
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")
    
    class Meta:
        verbose_name = "Log de Uso de API"
        verbose_name_plural = "Logs de Uso de API"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.provider.name} - {self.method} {self.endpoint} - {self.status_code}"
    
    @property
    def is_successful(self):
        return 200 <= self.status_code < 300


class ContentValidationRule(models.Model):
    """Regras de validação para conteúdo externo"""
    
    RULE_TYPES = [
        ('required_field', 'Campo Obrigatório'),
        ('field_format', 'Formato de Campo'),
        ('content_length', 'Tamanho do Conteúdo'),
        ('duplicate_check', 'Verificação de Duplicata'),
        ('quality_threshold', 'Limite de Qualidade'),
        ('keyword_presence', 'Presença de Palavra-chave'),
        ('blacklist_check', 'Verificação de Lista Negra'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(ExternalProvider, on_delete=models.CASCADE, related_name='validation_rules', verbose_name="Provedor")
    name = models.CharField(max_length=200, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    rule_type = models.CharField(max_length=30, choices=RULE_TYPES, verbose_name="Tipo de Regra")
    rule_config = models.JSONField(
        default=dict,
        help_text="Configuração específica da regra",
        verbose_name="Configuração da Regra"
    )
    
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    is_blocking = models.BooleanField(default=False, verbose_name="Bloqueia Importação")
    priority = models.PositiveIntegerField(default=0, verbose_name="Prioridade")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Regra de Validação"
        verbose_name_plural = "Regras de Validação"
        ordering = ['provider', 'priority']
    
    def __str__(self):
        return f"{self.provider.name} - {self.name}"


class ContentValidationResult(models.Model):
    """Resultados de validação de conteúdo"""
    
    STATUS_CHOICES = [
        ('passed', 'Aprovado'),
        ('failed', 'Reprovado'),
        ('warning', 'Aviso'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.ForeignKey(ExternalContent, on_delete=models.CASCADE, related_name='validation_results', verbose_name="Conteúdo")
    rule = models.ForeignKey(ContentValidationRule, on_delete=models.CASCADE, verbose_name="Regra")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Status")
    details = models.TextField(blank=True, verbose_name="Detalhes")
    score = models.FloatField(null=True, blank=True, verbose_name="Pontuação")
    
    validated_at = models.DateTimeField(auto_now_add=True, verbose_name="Validado em")
    
    class Meta:
        verbose_name = "Resultado de Validação"
        verbose_name_plural = "Resultados de Validação"
        ordering = ['-validated_at']
    
    def __str__(self):
        return f"{self.content.title} - {self.rule.name} - {self.status}"


class ExternalUserAccount(models.Model):
    """Contas de usuários em sistemas externos"""
    
    ACCOUNT_STATUS = [
        ('active', 'Ativa'),
        ('inactive', 'Inativa'),
        ('suspended', 'Suspensa'),
        ('expired', 'Expirada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='external_accounts', verbose_name="Usuário")
    provider = models.ForeignKey(ExternalProvider, on_delete=models.CASCADE, verbose_name="Provedor")
    
    # Identificação externa
    external_user_id = models.CharField(max_length=200, verbose_name="ID do Usuário Externo")
    external_username = models.CharField(max_length=200, blank=True, verbose_name="Nome de Usuário Externo")
    external_email = models.EmailField(blank=True, verbose_name="Email Externo")
    
    # Configurações da conta
    status = models.CharField(max_length=20, choices=ACCOUNT_STATUS, default='active', verbose_name="Status")
    access_token = models.TextField(blank=True, verbose_name="Token de Acesso")
    refresh_token = models.TextField(blank=True, verbose_name="Token de Atualização")
    token_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Token Expira em")
    
    # Permissões e escopo
    permissions = models.JSONField(
        default=list,
        help_text="Permissões concedidas pelo usuário",
        verbose_name="Permissões"
    )
    scopes = models.JSONField(
        default=list,
        help_text="Escopos de acesso",
        verbose_name="Escopos"
    )
    
    # Configurações de sincronização
    auto_sync = models.BooleanField(default=True, verbose_name="Sincronização Automática")
    last_sync = models.DateTimeField(null=True, blank=True, verbose_name="Última Sincronização")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Conta Externa"
        verbose_name_plural = "Contas Externas"
        unique_together = ['user', 'provider']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.provider.name}"
    
    @property
    def is_token_expired(self):
        if self.token_expires_at:
            return timezone.now() >= self.token_expires_at
        return False


class WebhookEndpoint(models.Model):
    """Endpoints de webhook para receber notificações de sistemas externos"""
    
    EVENT_TYPES = [
        ('content_updated', 'Conteúdo Atualizado'),
        ('content_deleted', 'Conteúdo Removido'),
        ('user_activity', 'Atividade do Usuário'),
        ('system_notification', 'Notificação do Sistema'),
        ('data_sync', 'Sincronização de Dados'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('suspended', 'Suspenso'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(ExternalProvider, on_delete=models.CASCADE, related_name='webhooks', verbose_name="Provedor")
    
    # Configurações do webhook
    event_types = models.JSONField(
        default=list,
        help_text="Tipos de eventos que o webhook deve receber",
        verbose_name="Tipos de Evento"
    )
    endpoint_url = models.URLField(verbose_name="URL do Endpoint")
    secret = models.CharField(max_length=200, verbose_name="Chave Secreta")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    
    # Estatísticas
    total_received = models.PositiveIntegerField(default=0, verbose_name="Total Recebidos")
    successful_processed = models.PositiveIntegerField(default=0, verbose_name="Processados com Sucesso")
    failed_processed = models.PositiveIntegerField(default=0, verbose_name="Falhas no Processamento")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Endpoint de Webhook"
        verbose_name_plural = "Endpoints de Webhook"
    
    def __str__(self):
        return f"{self.provider.name} - Webhook"


class WebhookEvent(models.Model):
    """Eventos recebidos via webhook"""
    
    STATUS_CHOICES = [
        ('received', 'Recebido'),
        ('processing', 'Processando'),
        ('processed', 'Processado'),
        ('failed', 'Falhou'),
        ('ignored', 'Ignorado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook = models.ForeignKey(WebhookEndpoint, on_delete=models.CASCADE, related_name='events', verbose_name="Webhook")
    
    # Dados do evento
    event_type = models.CharField(max_length=50, verbose_name="Tipo do Evento")
    event_id = models.CharField(max_length=200, blank=True, verbose_name="ID do Evento")
    payload = models.JSONField(verbose_name="Payload")
    headers = models.JSONField(default=dict, verbose_name="Cabeçalhos")
    
    # Processamento
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received', verbose_name="Status")
    processing_attempts = models.PositiveIntegerField(default=0, verbose_name="Tentativas de Processamento")
    error_message = models.TextField(blank=True, verbose_name="Mensagem de Erro")
    
    # Resultados
    actions_taken = models.JSONField(
        default=list,
        help_text="Ações realizadas em resposta ao evento",
        verbose_name="Ações Realizadas"
    )
    
    received_at = models.DateTimeField(auto_now_add=True, verbose_name="Recebido em")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Processado em")
    
    class Meta:
        verbose_name = "Evento de Webhook"
        verbose_name_plural = "Eventos de Webhook"
        ordering = ['-received_at']
    
    def __str__(self):
        return f"{self.webhook.provider.name} - {self.event_type} - {self.status}" 