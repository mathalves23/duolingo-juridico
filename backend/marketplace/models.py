"""
Sistema de Marketplace Avançado com IA e Blockchain
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class MarketplaceCategory(models.Model):
    """Categorias do marketplace"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Descrição")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Ícone")
    color = models.CharField(max_length=7, default="#3B82F6", verbose_name="Cor")
    
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="Categoria pai")
    
    is_active = models.BooleanField(default=True, verbose_name="Ativa")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class MarketplaceProduct(models.Model):
    """Produto do marketplace"""
    
    PRODUCT_TYPES = [
        ('course', 'Curso'),
        ('ebook', 'E-book'),
        ('video_series', 'Série de Vídeos'),
        ('question_bank', 'Banco de Questões'),
        ('study_plan', 'Plano de Estudos'),
        ('mentorship', 'Mentoria'),
        ('live_class', 'Aula Ao Vivo'),
        ('exam_simulation', 'Simulado'),
        ('ai_tutor', 'Tutor IA'),
        ('nft_certificate', 'Certificado NFT'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('pending_review', 'Aguardando Revisão'),
        ('approved', 'Aprovado'),
        ('published', 'Publicado'),
        ('suspended', 'Suspenso'),
        ('archived', 'Arquivado'),
    ]
    
    PRICING_MODELS = [
        ('one_time', 'Pagamento Único'),
        ('subscription', 'Assinatura'),
        ('pay_per_use', 'Pagar por Uso'),
        ('freemium', 'Freemium'),
        ('auction', 'Leilão'),
        ('nft_sale', 'Venda NFT'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Descrição")
    short_description = models.CharField(max_length=500, verbose_name="Descrição curta")
    
    # Categorização
    category = models.ForeignKey(MarketplaceCategory, on_delete=models.CASCADE, related_name='products', verbose_name="Categoria")
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, verbose_name="Tipo")
    tags = models.JSONField(default=list, verbose_name="Tags")
    
    # Vendedor
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_products', verbose_name="Vendedor")
    
    # Mídia
    thumbnail = models.ImageField(upload_to='marketplace/thumbnails/', verbose_name="Thumbnail")
    images = models.JSONField(default=list, verbose_name="Imagens adicionais")
    preview_video = models.URLField(blank=True, verbose_name="Vídeo de preview")
    
    # Preço e modelo
    pricing_model = models.CharField(max_length=20, choices=PRICING_MODELS, verbose_name="Modelo de precificação")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Preço")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Preço original")
    currency = models.CharField(max_length=3, default='BRL', verbose_name="Moeda")
    
    # Configurações de desconto
    discount_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)], verbose_name="Desconto (%)")
    discount_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Desconto expira em")
    
    # NFT/Blockchain
    is_nft = models.BooleanField(default=False, verbose_name="É NFT")
    nft_contract_address = models.CharField(max_length=42, blank=True, verbose_name="Endereço do contrato NFT")
    nft_token_id = models.CharField(max_length=100, blank=True, verbose_name="Token ID NFT")
    blockchain_network = models.CharField(max_length=50, blank=True, verbose_name="Rede blockchain")
    
    # Status e moderação
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Status")
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_products', verbose_name="Revisado por")
    review_notes = models.TextField(blank=True, verbose_name="Notas da revisão")
    
    # Estatísticas
    view_count = models.PositiveIntegerField(default=0, verbose_name="Visualizações")
    purchase_count = models.PositiveIntegerField(default=0, verbose_name="Compras")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="Avaliação")
    rating_count = models.PositiveIntegerField(default=0, verbose_name="Número de avaliações")
    
    # IA Features
    ai_generated_tags = models.JSONField(default=list, verbose_name="Tags geradas por IA")
    ai_difficulty_score = models.FloatField(null=True, blank=True, verbose_name="Score de dificuldade IA")
    ai_quality_score = models.FloatField(null=True, blank=True, verbose_name="Score de qualidade IA")
    ai_recommendation_score = models.FloatField(null=True, blank=True, verbose_name="Score de recomendação IA")
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True, verbose_name="Meta título")
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Meta descrição")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Publicado em")
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['rating', '-created_at']),
            models.Index(fields=['seller', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def current_price(self):
        if self.discount_percentage > 0 and (not self.discount_expires_at or self.discount_expires_at > timezone.now()):
            return self.price * (1 - self.discount_percentage / 100)
        return self.price
    
    @property
    def is_on_sale(self):
        return self.discount_percentage > 0 and (not self.discount_expires_at or self.discount_expires_at > timezone.now())


class MarketplacePurchase(models.Model):
    """Compra no marketplace"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
        ('refunded', 'Estornado'),
        ('disputed', 'Em Disputa'),
    ]
    
    PAYMENT_METHODS = [
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
        ('cryptocurrency', 'Criptomoeda'),
        ('platform_credits', 'Créditos da Plataforma'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_purchases', verbose_name="Comprador")
    product = models.ForeignKey(MarketplaceProduct, on_delete=models.CASCADE, related_name='purchases', verbose_name="Produto")
    
    # Detalhes da compra
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantidade")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço unitário")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço total")
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Desconto aplicado")
    
    # Pagamento
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="Método de pagamento")
    payment_id = models.CharField(max_length=200, blank=True, verbose_name="ID do pagamento")
    transaction_hash = models.CharField(max_length=100, blank=True, verbose_name="Hash da transação")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    
    # NFT/Blockchain
    nft_transferred = models.BooleanField(default=False, verbose_name="NFT transferido")
    buyer_wallet_address = models.CharField(max_length=42, blank=True, verbose_name="Endereço da carteira do comprador")
    
    # Comissões
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Taxa da plataforma")
    seller_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Ganhos do vendedor")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Concluído em")
    
    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.buyer.get_full_name()} - {self.product.title}"


class MarketplaceReview(models.Model):
    """Avaliação de produto"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(MarketplaceProduct, on_delete=models.CASCADE, related_name='reviews', verbose_name="Produto")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_reviews', verbose_name="Avaliador")
    purchase = models.ForeignKey(MarketplacePurchase, on_delete=models.CASCADE, related_name='reviews', verbose_name="Compra")
    
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Avaliação")
    title = models.CharField(max_length=200, verbose_name="Título")
    comment = models.TextField(verbose_name="Comentário")
    
    # Avaliações específicas
    content_quality = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Qualidade do conteúdo")
    value_for_money = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Custo-benefício")
    instructor_quality = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True, verbose_name="Qualidade do instrutor")
    
    # Interações
    helpful_count = models.PositiveIntegerField(default=0, verbose_name="Útil (contagem)")
    
    # IA Features
    ai_sentiment_score = models.FloatField(null=True, blank=True, verbose_name="Score de sentimento IA")
    ai_toxicity_score = models.FloatField(null=True, blank=True, verbose_name="Score de toxicidade IA")
    ai_verified_purchase = models.BooleanField(default=True, verbose_name="Compra verificada IA")
    
    # Moderação
    is_verified = models.BooleanField(default=True, verbose_name="Verificada")
    is_featured = models.BooleanField(default=False, verbose_name="Destacada")
    is_hidden = models.BooleanField(default=False, verbose_name="Oculta")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        unique_together = ['product', 'reviewer']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.title} - {self.rating}★"


class MarketplaceWishlist(models.Model):
    """Lista de desejos"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_wishlist', verbose_name="Usuário")
    product = models.ForeignKey(MarketplaceProduct, on_delete=models.CASCADE, related_name='wishlisted_by', verbose_name="Produto")
    
    # Configurações de notificação
    notify_on_sale = models.BooleanField(default=True, verbose_name="Notificar em promoção")
    notify_on_availability = models.BooleanField(default=True, verbose_name="Notificar disponibilidade")
    target_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Preço alvo")
    
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Adicionado em")
    
    class Meta:
        verbose_name = "Lista de Desejos"
        verbose_name_plural = "Listas de Desejos"
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.product.title}"


class MarketplaceCart(models.Model):
    """Carrinho de compras"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_cart', verbose_name="Usuário")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Carrinho"
        verbose_name_plural = "Carrinhos"
    
    def __str__(self):
        return f"Carrinho - {self.user.get_full_name()}"
    
    @property
    def total_items(self):
        return self.items.count()
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class MarketplaceCartItem(models.Model):
    """Item do carrinho"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(MarketplaceCart, on_delete=models.CASCADE, related_name='items', verbose_name="Carrinho")
    product = models.ForeignKey(MarketplaceProduct, on_delete=models.CASCADE, verbose_name="Produto")
    
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantidade")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço unitário")
    
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Adicionado em")
    
    class Meta:
        verbose_name = "Item do Carrinho"
        verbose_name_plural = "Itens do Carrinho"
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f"{self.product.title} x{self.quantity}"
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity


class MarketplacePromotion(models.Model):
    """Promoções e cupons"""
    
    PROMOTION_TYPES = [
        ('percentage', 'Desconto Percentual'),
        ('fixed_amount', 'Valor Fixo'),
        ('buy_one_get_one', 'Compre 1 Leve 2'),
        ('bundle', 'Pacote'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativa'),
        ('inactive', 'Inativa'),
        ('expired', 'Expirada'),
        ('used_up', 'Esgotada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nome")
    code = models.CharField(max_length=50, unique=True, verbose_name="Código")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPES, verbose_name="Tipo")
    
    # Configurações de desconto
    discount_percentage = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(100)], verbose_name="Desconto (%)")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Valor do desconto")
    
    # Condições
    minimum_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Compra mínima")
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Desconto máximo")
    
    # Produtos aplicáveis
    applicable_products = models.ManyToManyField(MarketplaceProduct, blank=True, verbose_name="Produtos aplicáveis")
    applicable_categories = models.ManyToManyField(MarketplaceCategory, blank=True, verbose_name="Categorias aplicáveis")
    
    # Limites
    usage_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name="Limite de uso")
    usage_count = models.PositiveIntegerField(default=0, verbose_name="Contagem de uso")
    user_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name="Limite por usuário")
    
    # Validade
    starts_at = models.DateTimeField(verbose_name="Inicia em")
    expires_at = models.DateTimeField(verbose_name="Expira em")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Promoção"
        verbose_name_plural = "Promoções"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def is_valid(self):
        now = timezone.now()
        return (
            self.status == 'active' and
            self.starts_at <= now <= self.expires_at and
            (not self.usage_limit or self.usage_count < self.usage_limit)
        )


class MarketplaceRecommendation(models.Model):
    """Recomendações de produtos baseadas em IA"""
    
    RECOMMENDATION_TYPES = [
        ('viewed_together', 'Visualizados Juntos'),
        ('bought_together', 'Comprados Juntos'),
        ('similar_users', 'Usuários Similares'),
        ('content_based', 'Baseado em Conteúdo'),
        ('trending', 'Em Alta'),
        ('personalized', 'Personalizada'),
        ('cross_sell', 'Venda Cruzada'),
        ('upsell', 'Upgrade'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_recommendations', verbose_name="Usuário")
    product = models.ForeignKey(MarketplaceProduct, on_delete=models.CASCADE, related_name='recommendations', verbose_name="Produto recomendado")
    
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES, verbose_name="Tipo")
    confidence_score = models.FloatField(verbose_name="Score de confiança")
    reason = models.TextField(verbose_name="Motivo")
    
    # Contexto da recomendação
    context_product = models.ForeignKey(MarketplaceProduct, on_delete=models.CASCADE, null=True, blank=True, related_name='context_recommendations', verbose_name="Produto de contexto")
    
    # Interações
    viewed = models.BooleanField(default=False, verbose_name="Visualizada")
    clicked = models.BooleanField(default=False, verbose_name="Clicada")
    purchased = models.BooleanField(default=False, verbose_name="Comprada")
    dismissed = models.BooleanField(default=False, verbose_name="Dispensada")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    expires_at = models.DateTimeField(verbose_name="Expira em")
    
    class Meta:
        verbose_name = "Recomendação"
        verbose_name_plural = "Recomendações"
        ordering = ['-confidence_score', '-created_at']
        unique_together = ['user', 'product', 'recommendation_type']
    
    def __str__(self):
        return f"Recomendação para {self.user.get_full_name()}: {self.product.title}"


class MarketplaceAnalytics(models.Model):
    """Analytics do marketplace"""
    
    EVENT_TYPES = [
        ('product_view', 'Visualização de Produto'),
        ('product_click', 'Clique em Produto'),
        ('add_to_cart', 'Adicionar ao Carrinho'),
        ('remove_from_cart', 'Remover do Carrinho'),
        ('add_to_wishlist', 'Adicionar à Lista de Desejos'),
        ('purchase_intent', 'Intenção de Compra'),
        ('search', 'Busca'),
        ('filter_apply', 'Aplicar Filtro'),
        ('recommendation_click', 'Clique em Recomendação'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='marketplace_analytics', verbose_name="Usuário")
    product = models.ForeignKey(MarketplaceProduct, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics', verbose_name="Produto")
    
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES, verbose_name="Tipo de evento")
    
    # Dados do evento
    event_data = models.JSONField(default=dict, verbose_name="Dados do evento")
    
    # Contexto
    session_id = models.UUIDField(verbose_name="ID da sessão")
    device_type = models.CharField(max_length=50, blank=True, verbose_name="Tipo de dispositivo")
    browser = models.CharField(max_length=100, blank=True, verbose_name="Navegador")
    referrer = models.URLField(blank=True, verbose_name="Referrer")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Analytics"
        verbose_name_plural = "Analytics"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['user', 'event_type']),
            models.Index(fields=['product', 'event_type']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}" 