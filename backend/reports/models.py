"""
Modelos para sistema de relatórios avançados do Duolingo Jurídico
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta, datetime
import json

User = get_user_model()


class ReportTemplate(models.Model):
    """Templates de relatórios"""
    
    REPORT_TYPES = [
        ('user_performance', 'Performance do Usuário'),
        ('system_analytics', 'Analytics do Sistema'),
        ('content_analysis', 'Análise de Conteúdo'),
        ('financial', 'Financeiro'),
        ('engagement', 'Engajamento'),
        ('learning_progress', 'Progresso de Aprendizado'),
        ('competitive_analysis', 'Análise Competitiva'),
        ('custom', 'Personalizado'),
    ]
    
    FREQUENCY_OPTIONS = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
        ('on_demand', 'Sob Demanda'),
    ]
    
    OUTPUT_FORMATS = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('html', 'HTML'),
        ('dashboard', 'Dashboard'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES, verbose_name="Tipo")
    
    # Configurações do template
    data_sources = models.JSONField(
        default=list,
        help_text="Fontes de dados para o relatório",
        verbose_name="Fontes de Dados"
    )
    metrics = models.JSONField(
        default=list,
        help_text="Métricas incluídas no relatório",
        verbose_name="Métricas"
    )
    filters = models.JSONField(
        default=dict,
        help_text="Filtros padrão do relatório",
        verbose_name="Filtros"
    )
    
    # Layout e formatação
    layout_config = models.JSONField(
        default=dict,
        help_text="Configuração de layout do relatório",
        verbose_name="Configuração de Layout"
    )
    chart_configs = models.JSONField(
        default=list,
        help_text="Configurações de gráficos",
        verbose_name="Configurações de Gráficos"
    )
    
    # Configurações de geração
    auto_generate = models.BooleanField(default=False, verbose_name="Geração Automática")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_OPTIONS, default='monthly', verbose_name="Frequência")
    output_format = models.CharField(max_length=20, choices=OUTPUT_FORMATS, default='pdf', verbose_name="Formato de Saída")
    
    # Permissões e acesso
    is_public = models.BooleanField(default=False, verbose_name="Público")
    allowed_users = models.ManyToManyField(User, blank=True, related_name='allowed_reports', verbose_name="Usuários Permitidos")
    required_permissions = models.JSONField(
        default=list,
        help_text="Permissões necessárias para visualizar",
        verbose_name="Permissões Necessárias"
    )
    
    # Metadados
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports', verbose_name="Criado por")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Template de Relatório"
        verbose_name_plural = "Templates de Relatórios"
        ordering = ['report_type', 'sort_order', 'name']
    
    def __str__(self):
        return self.name


class GeneratedReport(models.Model):
    """Relatórios gerados"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('generating', 'Gerando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
        ('expired', 'Expirado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='generated_reports', verbose_name="Template")
    
    # Identificação
    title = models.CharField(max_length=300, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    # Configurações da geração
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_reports', verbose_name="Solicitado por")
    filters_applied = models.JSONField(
        default=dict,
        help_text="Filtros aplicados na geração",
        verbose_name="Filtros Aplicados"
    )
    date_range_start = models.DateTimeField(verbose_name="Início do Período")
    date_range_end = models.DateTimeField(verbose_name="Fim do Período")
    
    # Status e processamento
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    progress_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)], verbose_name="Progresso (%)")
    
    # Dados do relatório
    data = models.JSONField(
        default=dict,
        help_text="Dados processados do relatório",
        verbose_name="Dados"
    )
    summary_stats = models.JSONField(
        default=dict,
        help_text="Estatísticas resumidas",
        verbose_name="Estatísticas Resumidas"
    )
    
    # Arquivo gerado
    file_path = models.CharField(max_length=500, blank=True, verbose_name="Caminho do Arquivo")
    file_size_bytes = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tamanho do Arquivo (bytes)")
    file_format = models.CharField(max_length=20, blank=True, verbose_name="Formato do Arquivo")
    
    # Metadados de processamento
    generation_time_seconds = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tempo de Geração (segundos)")
    error_message = models.TextField(blank=True, verbose_name="Mensagem de Erro")
    
    # Acesso e compartilhamento
    is_public = models.BooleanField(default=False, verbose_name="Público")
    shared_with = models.ManyToManyField(User, blank=True, related_name='shared_reports', verbose_name="Compartilhado com")
    access_count = models.PositiveIntegerField(default=0, verbose_name="Contagem de Acessos")
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="Solicitado em")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Iniciado em")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Concluído em")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expira em")
    
    class Meta:
        verbose_name = "Relatório Gerado"
        verbose_name_plural = "Relatórios Gerados"
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.title} - {self.status}"
    
    @property
    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at
    
    def mark_as_started(self):
        """Marca o relatório como iniciado"""
        self.status = 'generating'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
    
    def mark_as_completed(self):
        """Marca o relatório como concluído"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.progress_percentage = 100
        if self.started_at:
            self.generation_time_seconds = int((self.completed_at - self.started_at).total_seconds())
        self.save(update_fields=['status', 'completed_at', 'progress_percentage', 'generation_time_seconds'])


class Dashboard(models.Model):
    """Dashboards personalizados"""
    
    DASHBOARD_TYPES = [
        ('personal', 'Pessoal'),
        ('administrative', 'Administrativo'),
        ('academic', 'Acadêmico'),
        ('financial', 'Financeiro'),
        ('operational', 'Operacional'),
    ]
    
    ACCESS_LEVELS = [
        ('private', 'Privado'),
        ('shared', 'Compartilhado'),
        ('public', 'Público'),
        ('admin_only', 'Apenas Admins'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    dashboard_type = models.CharField(max_length=20, choices=DASHBOARD_TYPES, verbose_name="Tipo")
    
    # Proprietário e acesso
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_dashboards', verbose_name="Proprietário")
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='private', verbose_name="Nível de Acesso")
    shared_with = models.ManyToManyField(User, blank=True, related_name='shared_dashboards', verbose_name="Compartilhado com")
    
    # Configuração do layout
    layout_config = models.JSONField(
        default=dict,
        help_text="Configuração de layout do dashboard",
        verbose_name="Configuração de Layout"
    )
    widgets = models.JSONField(
        default=list,
        help_text="Widgets do dashboard",
        verbose_name="Widgets"
    )
    
    # Configurações de atualização
    auto_refresh = models.BooleanField(default=True, verbose_name="Atualização Automática")
    refresh_interval_minutes = models.PositiveIntegerField(default=30, verbose_name="Intervalo de Atualização (minutos)")
    last_updated = models.DateTimeField(null=True, blank=True, verbose_name="Última Atualização")
    
    # Metadados
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    is_default = models.BooleanField(default=False, verbose_name="Padrão")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    
    # Estatísticas de uso
    view_count = models.PositiveIntegerField(default=0, verbose_name="Visualizações")
    last_viewed = models.DateTimeField(null=True, blank=True, verbose_name="Última Visualização")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboards"
        ordering = ['owner', 'sort_order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.owner.get_full_name()})"
    
    def can_view(self, user):
        """Verifica se um usuário pode visualizar o dashboard"""
        if self.owner == user:
            return True
        if self.access_level == 'public':
            return True
        if self.access_level == 'shared' and user in self.shared_with.all():
            return True
        if self.access_level == 'admin_only' and user.is_staff:
            return True
        return False


class Widget(models.Model):
    """Widgets para dashboards"""
    
    WIDGET_TYPES = [
        ('chart', 'Gráfico'),
        ('metric', 'Métrica'),
        ('table', 'Tabela'),
        ('progress', 'Progresso'),
        ('text', 'Texto'),
        ('image', 'Imagem'),
        ('calendar', 'Calendário'),
        ('feed', 'Feed'),
        ('map', 'Mapa'),
    ]
    
    CHART_TYPES = [
        ('line', 'Linha'),
        ('bar', 'Barras'),
        ('pie', 'Pizza'),
        ('donut', 'Rosca'),
        ('area', 'Área'),
        ('scatter', 'Dispersão'),
        ('gauge', 'Velocímetro'),
        ('funnel', 'Funil'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='dashboard_widgets', verbose_name="Dashboard")
    
    # Configurações básicas
    title = models.CharField(max_length=200, verbose_name="Título")
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, verbose_name="Tipo")
    
    # Posição e tamanho
    position_x = models.PositiveIntegerField(default=0, verbose_name="Posição X")
    position_y = models.PositiveIntegerField(default=0, verbose_name="Posição Y")
    width = models.PositiveIntegerField(default=4, verbose_name="Largura")
    height = models.PositiveIntegerField(default=3, verbose_name="Altura")
    
    # Configurações específicas do widget
    data_source = models.CharField(max_length=200, verbose_name="Fonte de Dados")
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, blank=True, verbose_name="Tipo de Gráfico")
    config = models.JSONField(
        default=dict,
        help_text="Configurações específicas do widget",
        verbose_name="Configuração"
    )
    
    # Filtros e parâmetros
    filters = models.JSONField(
        default=dict,
        help_text="Filtros aplicados aos dados",
        verbose_name="Filtros"
    )
    parameters = models.JSONField(
        default=dict,
        help_text="Parâmetros do widget",
        verbose_name="Parâmetros"
    )
    
    # Cache de dados
    cached_data = models.JSONField(
        default=dict,
        help_text="Dados em cache do widget",
        verbose_name="Dados em Cache"
    )
    cache_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Cache Expira em")
    
    # Metadados
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    refresh_interval_minutes = models.PositiveIntegerField(default=30, verbose_name="Intervalo de Atualização (minutos)")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Widget"
        verbose_name_plural = "Widgets"
        ordering = ['dashboard', 'position_y', 'position_x']
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.title}"
    
    @property
    def is_cache_expired(self):
        return self.cache_expires_at and timezone.now() > self.cache_expires_at


class MetricDefinition(models.Model):
    """Definições de métricas disponíveis"""
    
    METRIC_TYPES = [
        ('count', 'Contagem'),
        ('sum', 'Soma'),
        ('average', 'Média'),
        ('percentage', 'Porcentagem'),
        ('ratio', 'Proporção'),
        ('growth', 'Crescimento'),
        ('custom', 'Personalizada'),
    ]
    
    DATA_TYPES = [
        ('integer', 'Inteiro'),
        ('decimal', 'Decimal'),
        ('percentage', 'Porcentagem'),
        ('currency', 'Moeda'),
        ('duration', 'Duração'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES, verbose_name="Tipo")
    
    # Configuração da métrica
    data_source = models.CharField(max_length=200, verbose_name="Fonte de Dados")
    calculation_method = models.TextField(verbose_name="Método de Cálculo")
    data_type = models.CharField(max_length=20, choices=DATA_TYPES, verbose_name="Tipo de Dados")
    
    # Formatação
    format_string = models.CharField(max_length=50, default='{value}', verbose_name="String de Formatação")
    unit = models.CharField(max_length=20, blank=True, verbose_name="Unidade")
    
    # Configurações de cálculo
    aggregation_period = models.CharField(
        max_length=20,
        choices=[
            ('real_time', 'Tempo Real'),
            ('hourly', 'Por Hora'),
            ('daily', 'Diário'),
            ('weekly', 'Semanal'),
            ('monthly', 'Mensal'),
        ],
        default='daily',
        verbose_name="Período de Agregação"
    )
    
    # Validação e limites
    min_value = models.FloatField(null=True, blank=True, verbose_name="Valor Mínimo")
    max_value = models.FloatField(null=True, blank=True, verbose_name="Valor Máximo")
    warning_threshold = models.FloatField(null=True, blank=True, verbose_name="Limite de Aviso")
    critical_threshold = models.FloatField(null=True, blank=True, verbose_name="Limite Crítico")
    
    # Metadados
    category = models.CharField(max_length=100, verbose_name="Categoria")
    tags = models.JSONField(default=list, verbose_name="Tags")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Criado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Definição de Métrica"
        verbose_name_plural = "Definições de Métricas"
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name


class MetricValue(models.Model):
    """Valores históricos de métricas"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric = models.ForeignKey(MetricDefinition, on_delete=models.CASCADE, related_name='values', verbose_name="Métrica")
    
    # Valor da métrica
    value = models.FloatField(verbose_name="Valor")
    formatted_value = models.CharField(max_length=100, verbose_name="Valor Formatado")
    
    # Dimensões (para segmentação)
    dimensions = models.JSONField(
        default=dict,
        help_text="Dimensões para segmentação (ex: {user_id: 123, subject: 'Direito Civil'})",
        verbose_name="Dimensões"
    )
    
    # Metadados
    calculation_details = models.JSONField(
        default=dict,
        help_text="Detalhes do cálculo",
        verbose_name="Detalhes do Cálculo"
    )
    
    # Timestamps
    period_start = models.DateTimeField(verbose_name="Início do Período")
    period_end = models.DateTimeField(verbose_name="Fim do Período")
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="Calculado em")
    
    class Meta:
        verbose_name = "Valor de Métrica"
        verbose_name_plural = "Valores de Métricas"
        unique_together = ['metric', 'period_start', 'period_end', 'dimensions']
        ordering = ['-period_start']
    
    def __str__(self):
        return f"{self.metric.name}: {self.formatted_value} ({self.period_start.date()})"


class ReportSchedule(models.Model):
    """Agendamento de relatórios automáticos"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    ]
    
    DELIVERY_METHODS = [
        ('email', 'Email'),
        ('dashboard', 'Dashboard'),
        ('file_storage', 'Armazenamento de Arquivo'),
        ('api_webhook', 'Webhook API'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='schedules', verbose_name="Template")
    
    # Configurações de agendamento
    name = models.CharField(max_length=200, verbose_name="Nome")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name="Frequência")
    
    # Configurações de horário
    time_of_day = models.TimeField(verbose_name="Horário do Dia")
    day_of_week = models.PositiveIntegerField(
        null=True, blank=True,
        choices=[(i, d) for i, d in enumerate(['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'])],
        verbose_name="Dia da Semana"
    )
    day_of_month = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name="Dia do Mês"
    )
    
    # Configurações de entrega
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHODS, verbose_name="Método de Entrega")
    recipients = models.ManyToManyField(User, related_name='scheduled_reports', verbose_name="Destinatários")
    email_addresses = models.JSONField(
        default=list,
        help_text="Endereços de email adicionais",
        verbose_name="Emails Adicionais"
    )
    webhook_url = models.URLField(blank=True, verbose_name="URL do Webhook")
    
    # Configurações de conteúdo
    filters = models.JSONField(
        default=dict,
        help_text="Filtros a serem aplicados",
        verbose_name="Filtros"
    )
    include_summary = models.BooleanField(default=True, verbose_name="Incluir Resumo")
    include_charts = models.BooleanField(default=True, verbose_name="Incluir Gráficos")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    last_run = models.DateTimeField(null=True, blank=True, verbose_name="Última Execução")
    next_run = models.DateTimeField(null=True, blank=True, verbose_name="Próxima Execução")
    
    # Estatísticas
    total_runs = models.PositiveIntegerField(default=0, verbose_name="Total de Execuções")
    successful_runs = models.PositiveIntegerField(default=0, verbose_name="Execuções Bem-sucedidas")
    failed_runs = models.PositiveIntegerField(default=0, verbose_name="Execuções Falhadas")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_schedules', verbose_name="Criado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Agendamento de Relatório"
        verbose_name_plural = "Agendamentos de Relatórios"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.frequency})"


class AlertRule(models.Model):
    """Regras de alerta baseadas em métricas"""
    
    CONDITION_TYPES = [
        ('greater_than', 'Maior que'),
        ('less_than', 'Menor que'),
        ('equal_to', 'Igual a'),
        ('not_equal_to', 'Diferente de'),
        ('between', 'Entre'),
        ('percentage_change', 'Mudança Percentual'),
    ]
    
    SEVERITY_LEVELS = [
        ('info', 'Informação'),
        ('warning', 'Aviso'),
        ('critical', 'Crítico'),
        ('emergency', 'Emergência'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    # Métrica monitorada
    metric = models.ForeignKey(MetricDefinition, on_delete=models.CASCADE, related_name='alert_rules', verbose_name="Métrica")
    
    # Condições do alerta
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPES, verbose_name="Tipo de Condição")
    threshold_value = models.FloatField(verbose_name="Valor Limite")
    threshold_value_2 = models.FloatField(null=True, blank=True, verbose_name="Valor Limite 2")
    
    # Configurações do alerta
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, verbose_name="Severidade")
    evaluation_period_minutes = models.PositiveIntegerField(default=15, verbose_name="Período de Avaliação (minutos)")
    minimum_breach_duration_minutes = models.PositiveIntegerField(default=5, verbose_name="Duração Mínima de Violação (minutos)")
    
    # Filtros de dimensão
    dimension_filters = models.JSONField(
        default=dict,
        help_text="Filtros por dimensão",
        verbose_name="Filtros de Dimensão"
    )
    
    # Configurações de notificação
    notification_channels = models.JSONField(
        default=list,
        help_text="Canais de notificação",
        verbose_name="Canais de Notificação"
    )
    notification_users = models.ManyToManyField(User, blank=True, related_name='alert_notifications', verbose_name="Usuários para Notificar")
    
    # Configurações de supressão
    cooldown_period_minutes = models.PositiveIntegerField(default=60, verbose_name="Período de Silêncio (minutos)")
    max_notifications_per_hour = models.PositiveIntegerField(default=10, verbose_name="Máximo de Notificações por Hora")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    last_triggered = models.DateTimeField(null=True, blank=True, verbose_name="Último Disparo")
    last_evaluated = models.DateTimeField(null=True, blank=True, verbose_name="Última Avaliação")
    
    # Estatísticas
    total_triggers = models.PositiveIntegerField(default=0, verbose_name="Total de Disparos")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Criado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Regra de Alerta"
        verbose_name_plural = "Regras de Alerta"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class AlertInstance(models.Model):
    """Instâncias de alertas disparados"""
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('resolved', 'Resolvido'),
        ('acknowledged', 'Reconhecido'),
        ('silenced', 'Silenciado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, related_name='instances', verbose_name="Regra")
    
    # Status e detalhes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    message = models.TextField(verbose_name="Mensagem")
    
    # Valores que causaram o alerta
    trigger_value = models.FloatField(verbose_name="Valor que Disparou")
    threshold_value = models.FloatField(verbose_name="Valor Limite")
    dimensions = models.JSONField(default=dict, verbose_name="Dimensões")
    
    # Timestamps
    triggered_at = models.DateTimeField(auto_now_add=True, verbose_name="Disparado em")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Resolvido em")
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name="Reconhecido em")
    acknowledged_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Reconhecido por")
    
    # Notificações enviadas
    notifications_sent = models.JSONField(
        default=list,
        help_text="Log de notificações enviadas",
        verbose_name="Notificações Enviadas"
    )
    
    class Meta:
        verbose_name = "Instância de Alerta"
        verbose_name_plural = "Instâncias de Alerta"
        ordering = ['-triggered_at']
    
    def __str__(self):
        return f"{self.rule.name} - {self.status} ({self.triggered_at})"
    
    def acknowledge(self, user):
        """Reconhece o alerta"""
        self.status = 'acknowledged'
        self.acknowledged_at = timezone.now()
        self.acknowledged_by = user
        self.save(update_fields=['status', 'acknowledged_at', 'acknowledged_by'])
    
    def resolve(self):
        """Resolve o alerta"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolved_at']) 