"""
Sistema de Integração Institucional e Expansão Regional
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class InstitutionType(models.Model):
    """Tipos de instituições"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    # Configurações específicas
    requires_approval = models.BooleanField(default=True, verbose_name="Requer aprovação")
    supports_sso = models.BooleanField(default=False, verbose_name="Suporta SSO")
    api_integration = models.BooleanField(default=False, verbose_name="Integração API")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Tipo de Instituição"
        verbose_name_plural = "Tipos de Instituições"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Region(models.Model):
    """Regiões geográficas"""
    
    REGION_LEVELS = [
        ('country', 'País'),
        ('state', 'Estado'),
        ('city', 'Cidade'),
        ('district', 'Distrito'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nome")
    code = models.CharField(max_length=10, verbose_name="Código")
    level = models.CharField(max_length=20, choices=REGION_LEVELS, verbose_name="Nível")
    
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="Região pai")
    
    # Dados geográficos
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, verbose_name="Longitude")
    timezone = models.CharField(max_length=50, default='America/Sao_Paulo', verbose_name="Fuso horário")
    
    # Configurações regionais
    language = models.CharField(max_length=10, default='pt-BR', verbose_name="Idioma")
    currency = models.CharField(max_length=3, default='BRL', verbose_name="Moeda")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    is_supported = models.BooleanField(default=False, verbose_name="Suportado")
    launch_date = models.DateField(null=True, blank=True, verbose_name="Data de lançamento")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Região"
        verbose_name_plural = "Regiões"
        ordering = ['level', 'name']
        unique_together = ['code', 'level']
    
    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"


class Institution(models.Model):
    """Instituições parceiras"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovada'),
        ('active', 'Ativa'),
        ('suspended', 'Suspensa'),
        ('terminated', 'Terminada'),
    ]
    
    PARTNERSHIP_TYPES = [
        ('educational', 'Educacional'),
        ('government', 'Governamental'),
        ('judicial', 'Judicial'),
        ('private', 'Privada'),
        ('non_profit', 'Sem fins lucrativos'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nome")
    legal_name = models.CharField(max_length=200, verbose_name="Razão social")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    
    # Classificação
    institution_type = models.ForeignKey(InstitutionType, on_delete=models.CASCADE, verbose_name="Tipo")
    partnership_type = models.CharField(max_length=20, choices=PARTNERSHIP_TYPES, verbose_name="Tipo de parceria")
    
    # Localização
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name="Região")
    address = models.TextField(verbose_name="Endereço")
    
    # Contato
    contact_email = models.EmailField(verbose_name="Email de contato")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    website = models.URLField(blank=True, verbose_name="Website")
    
    # Representante
    representative = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='represented_institutions', verbose_name="Representante")
    
    # Configurações
    logo = models.ImageField(upload_to='institutions/logos/', blank=True, verbose_name="Logo")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    # Status da parceria
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    contract_start_date = models.DateField(null=True, blank=True, verbose_name="Início do contrato")
    contract_end_date = models.DateField(null=True, blank=True, verbose_name="Fim do contrato")
    
    # Integração técnica
    api_key = models.CharField(max_length=100, blank=True, verbose_name="Chave API")
    sso_enabled = models.BooleanField(default=False, verbose_name="SSO habilitado")
    sso_metadata = models.JSONField(default=dict, verbose_name="Metadados SSO")
    
    # Configurações de conteúdo
    custom_branding = models.BooleanField(default=False, verbose_name="Marca personalizada")
    content_filters = models.JSONField(default=dict, verbose_name="Filtros de conteúdo")
    access_permissions = models.JSONField(default=dict, verbose_name="Permissões de acesso")
    
    # Métricas
    total_users = models.PositiveIntegerField(default=0, verbose_name="Total de usuários")
    active_users = models.PositiveIntegerField(default=0, verbose_name="Usuários ativos")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Instituição"
        verbose_name_plural = "Instituições"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class InstitutionalUser(models.Model):
    """Usuários vinculados a instituições"""
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('suspended', 'Suspenso'),
        ('graduated', 'Formado'),
        ('transferred', 'Transferido'),
    ]
    
    ROLE_CHOICES = [
        ('student', 'Estudante'),
        ('instructor', 'Instrutor'),
        ('admin', 'Administrador'),
        ('coordinator', 'Coordenador'),
        ('guest', 'Convidado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='institutional_affiliations', verbose_name="Usuário")
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='users', verbose_name="Instituição")
    
    # Dados institucionais
    institutional_id = models.CharField(max_length=50, verbose_name="ID institucional")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Papel")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    
    # Datas
    enrollment_date = models.DateField(verbose_name="Data de matrícula")
    graduation_date = models.DateField(null=True, blank=True, verbose_name="Data de formatura")
    
    # Configurações específicas
    access_level = models.JSONField(default=dict, verbose_name="Nível de acesso")
    custom_permissions = models.JSONField(default=dict, verbose_name="Permissões customizadas")
    
    # Metadados
    metadata = models.JSONField(default=dict, verbose_name="Metadados")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Usuário Institucional"
        verbose_name_plural = "Usuários Institucionais"
        unique_together = ['user', 'institution']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.institution.name}"


class RegionalContent(models.Model):
    """Conteúdo específico por região"""
    
    CONTENT_TYPES = [
        ('legislation', 'Legislação'),
        ('exam_info', 'Informações de Concurso'),
        ('local_news', 'Notícias Locais'),
        ('study_groups', 'Grupos de Estudo'),
        ('events', 'Eventos'),
        ('job_openings', 'Vagas'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Título")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, verbose_name="Tipo de conteúdo")
    
    # Localização
    regions = models.ManyToManyField(Region, verbose_name="Regiões")
    
    # Conteúdo
    description = models.TextField(verbose_name="Descrição")
    content_data = models.JSONField(default=dict, verbose_name="Dados do conteúdo")
    attachments = models.JSONField(default=list, verbose_name="Anexos")
    
    # Configurações
    is_featured = models.BooleanField(default=False, verbose_name="Destacado")
    is_urgent = models.BooleanField(default=False, verbose_name="Urgente")
    priority = models.PositiveIntegerField(default=0, verbose_name="Prioridade")
    
    # Datas
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Publicado em")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expira em")
    
    # Autor
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")
    
    # Aprovação
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_content', verbose_name="Aprovado por")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Aprovado em")
    
    # Métricas
    view_count = models.PositiveIntegerField(default=0, verbose_name="Visualizações")
    engagement_score = models.FloatField(default=0.0, verbose_name="Score de engajamento")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Conteúdo Regional"
        verbose_name_plural = "Conteúdos Regionais"
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return self.title


class PartnershipAgreement(models.Model):
    """Acordos de parceria"""
    
    AGREEMENT_TYPES = [
        ('basic', 'Básico'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
        ('custom', 'Personalizado'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('pending_review', 'Aguardando Revisão'),
        ('approved', 'Aprovado'),
        ('active', 'Ativo'),
        ('expired', 'Expirado'),
        ('terminated', 'Terminado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='agreements', verbose_name="Instituição")
    
    # Detalhes do acordo
    agreement_type = models.CharField(max_length=20, choices=AGREEMENT_TYPES, verbose_name="Tipo de acordo")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    
    # Termos comerciais
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Taxa mensal")
    setup_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Taxa de setup")
    user_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name="Limite de usuários")
    
    # Recursos incluídos
    included_features = models.JSONField(default=list, verbose_name="Recursos incluídos")
    custom_features = models.JSONField(default=list, verbose_name="Recursos customizados")
    support_level = models.CharField(max_length=20, default='standard', verbose_name="Nível de suporte")
    
    # Datas
    start_date = models.DateField(verbose_name="Data de início")
    end_date = models.DateField(verbose_name="Data de fim")
    renewal_date = models.DateField(null=True, blank=True, verbose_name="Data de renovação")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Status")
    
    # Aprovações
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_agreements', verbose_name="Criado por")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_agreements', verbose_name="Aprovado por")
    
    # Documentos
    contract_document = models.FileField(upload_to='agreements/contracts/', blank=True, verbose_name="Documento do contrato")
    signed_document = models.FileField(upload_to='agreements/signed/', blank=True, verbose_name="Documento assinado")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Acordo de Parceria"
        verbose_name_plural = "Acordos de Parceria"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.institution.name} - {self.title}"


class RegionalLaunch(models.Model):
    """Lançamentos regionais"""
    
    LAUNCH_PHASES = [
        ('planning', 'Planejamento'),
        ('development', 'Desenvolvimento'),
        ('testing', 'Testes'),
        ('soft_launch', 'Lançamento Suave'),
        ('full_launch', 'Lançamento Completo'),
        ('maintenance', 'Manutenção'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='launches', verbose_name="Região")
    
    # Detalhes do lançamento
    name = models.CharField(max_length=200, verbose_name="Nome")
    description = models.TextField(verbose_name="Descrição")
    phase = models.CharField(max_length=20, choices=LAUNCH_PHASES, verbose_name="Fase")
    
    # Datas planejadas
    planned_start_date = models.DateField(verbose_name="Data planejada de início")
    planned_launch_date = models.DateField(verbose_name="Data planejada de lançamento")
    actual_launch_date = models.DateField(null=True, blank=True, verbose_name="Data real de lançamento")
    
    # Recursos específicos
    localized_content = models.BooleanField(default=False, verbose_name="Conteúdo localizado")
    local_partnerships = models.BooleanField(default=False, verbose_name="Parcerias locais")
    marketing_campaign = models.BooleanField(default=False, verbose_name="Campanha de marketing")
    
    # Metas
    target_users = models.PositiveIntegerField(verbose_name="Meta de usuários")
    target_revenue = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Meta de receita")
    
    # Progresso
    current_users = models.PositiveIntegerField(default=0, verbose_name="Usuários atuais")
    current_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Receita atual")
    
    # Equipe
    project_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_launches', verbose_name="Gerente do projeto")
    team_members = models.ManyToManyField(User, blank=True, verbose_name="Membros da equipe")
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    completion_percentage = models.PositiveIntegerField(default=0, verbose_name="Porcentagem de conclusão")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Lançamento Regional"
        verbose_name_plural = "Lançamentos Regionais"
        ordering = ['-planned_launch_date']
    
    def __str__(self):
        return f"{self.name} - {self.region.name}"


class InstitutionalAnalytics(models.Model):
    """Analytics por instituição"""
    
    METRIC_TYPES = [
        ('user_engagement', 'Engajamento de Usuários'),
        ('content_consumption', 'Consumo de Conteúdo'),
        ('performance_metrics', 'Métricas de Performance'),
        ('revenue_metrics', 'Métricas de Receita'),
        ('support_metrics', 'Métricas de Suporte'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='analytics', verbose_name="Instituição")
    
    # Período
    date = models.DateField(verbose_name="Data")
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES, verbose_name="Tipo de métrica")
    
    # Dados
    metrics_data = models.JSONField(default=dict, verbose_name="Dados das métricas")
    
    # Comparações
    previous_period_data = models.JSONField(default=dict, verbose_name="Dados do período anterior")
    growth_percentage = models.FloatField(default=0.0, verbose_name="Porcentagem de crescimento")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Analytics Institucional"
        verbose_name_plural = "Analytics Institucionais"
        unique_together = ['institution', 'date', 'metric_type']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.institution.name} - {self.metric_type} ({self.date})"


class RegionalSupport(models.Model):
    """Suporte regional"""
    
    SUPPORT_TYPES = [
        ('technical', 'Técnico'),
        ('educational', 'Educacional'),
        ('commercial', 'Comercial'),
        ('implementation', 'Implementação'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('planning', 'Planejando'),
        ('on_hold', 'Em Espera'),
        ('completed', 'Concluído'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='support_initiatives', verbose_name="Região")
    
    # Detalhes
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    support_type = models.CharField(max_length=20, choices=SUPPORT_TYPES, verbose_name="Tipo de suporte")
    
    # Recursos
    allocated_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Orçamento alocado")
    team_size = models.PositiveIntegerField(default=1, verbose_name="Tamanho da equipe")
    
    # Cronograma
    start_date = models.DateField(verbose_name="Data de início")
    end_date = models.DateField(verbose_name="Data de fim")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning', verbose_name="Status")
    
    # Responsável
    coordinator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Coordenador")
    
    # Métricas
    institutions_supported = models.PositiveIntegerField(default=0, verbose_name="Instituições apoiadas")
    users_impacted = models.PositiveIntegerField(default=0, verbose_name="Usuários impactados")
    success_rate = models.FloatField(default=0.0, verbose_name="Taxa de sucesso")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Suporte Regional"
        verbose_name_plural = "Suportes Regionais"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.region.name}" 