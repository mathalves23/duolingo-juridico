"""
Modelos para sistema de pagamentos e assinaturas
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class PaymentProvider(models.Model):
    """Provedores de pagamento (Stripe, PagarMe, etc.)"""
    
    PROVIDER_CHOICES = [
        ('stripe', 'Stripe'),
        ('pagarme', 'PagarMe'),
        ('mercadopago', 'Mercado Pago'),
        ('pagseguro', 'PagSeguro'),
        ('picpay', 'PicPay'),
    ]
    
    name = models.CharField(max_length=50, choices=PROVIDER_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    api_key = models.TextField(blank=True)
    secret_key = models.TextField(blank=True)
    webhook_url = models.URLField(blank=True)
    
    # Configurações específicas
    supports_pix = models.BooleanField(default=False)
    supports_boleto = models.BooleanField(default=False)
    supports_credit_card = models.BooleanField(default=True)
    supports_installments = models.BooleanField(default=False)
    max_installments = models.PositiveIntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Provedor de Pagamento'
        verbose_name_plural = 'Provedores de Pagamento'
    
    def __str__(self):
        return self.display_name


class SubscriptionPlan(models.Model):
    """Planos de assinatura"""
    
    PLAN_TYPES = [
        ('free', 'Gratuito'),
        ('basic', 'Básico'),
        ('premium', 'Premium'),
        ('premium_plus', 'Premium Plus'),
        ('enterprise', 'Empresarial'),
    ]
    
    BILLING_CYCLES = [
        ('monthly', 'Mensal'),
        ('quarterly', 'Trimestral'),
        ('semiannual', 'Semestral'),
        ('annual', 'Anual'),
        ('lifetime', 'Vitalício'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES)
    
    # Features
    max_questions_per_day = models.PositiveIntegerField(null=True, blank=True)  # null = unlimited
    max_simulations_per_month = models.PositiveIntegerField(null=True, blank=True)
    has_ai_explanations = models.BooleanField(default=False)
    has_study_plans = models.BooleanField(default=False)
    has_progress_analytics = models.BooleanField(default=False)
    has_offline_access = models.BooleanField(default=False)
    has_priority_support = models.BooleanField(default=False)
    has_custom_reminders = models.BooleanField(default=False)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    # Trial
    has_trial = models.BooleanField(default=False)
    trial_days = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Plano de Assinatura'
        verbose_name_plural = 'Planos de Assinatura'
        ordering = ['sort_order', 'price']
    
    def __str__(self):
        return f"{self.name} - R$ {self.price}/{self.get_billing_cycle_display()}"
    
    @property
    def discount_percentage(self):
        if self.original_price and self.price < self.original_price:
            return round(((self.original_price - self.price) / self.original_price) * 100)
        return 0


class Payment(models.Model):
    """Registro de pagamentos"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Completo'),
        ('failed', 'Falhou'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Estornado'),
        ('partially_refunded', 'Parcialmente Estornado'),
    ]
    
    PAYMENT_METHODS = [
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Transferência Bancária'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    provider = models.ForeignKey(PaymentProvider, on_delete=models.CASCADE)
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BRL')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    installments = models.PositiveIntegerField(default=1)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # External references
    external_payment_id = models.CharField(max_length=255, blank=True)
    external_customer_id = models.CharField(max_length=255, blank=True)
    
    # Metadata
    payment_data = models.JSONField(default=dict)  # Store provider-specific data
    webhook_data = models.JSONField(default=dict)  # Store webhook responses
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['external_payment_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Pagamento {self.id} - {self.user.email} - R$ {self.amount}"
    
    def mark_as_paid(self):
        self.status = 'completed'
        self.paid_at = timezone.now()
        self.save()


class Subscription(models.Model):
    """Assinaturas dos usuários"""
    
    STATUS_CHOICES = [
        ('trial', 'Período de Teste'),
        ('active', 'Ativa'),
        ('past_due', 'Em Atraso'),
        ('cancelled', 'Cancelada'),
        ('expired', 'Expirada'),
        ('suspended', 'Suspensa'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    
    # Dates
    started_at = models.DateTimeField(auto_now_add=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)  # For cancelled subscriptions
    
    # Billing
    last_payment = models.ForeignKey(
        Payment, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='active_subscription'
    )
    next_billing_date = models.DateTimeField(null=True, blank=True)
    
    # Configuration
    auto_renew = models.BooleanField(default=True)
    cancel_at_period_end = models.BooleanField(default=False)
    
    # External references
    external_subscription_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Assinatura {self.user.email} - {self.plan.name}"
    
    @property
    def is_active(self):
        return self.status == 'active' and self.current_period_end > timezone.now()
    
    @property
    def is_trial(self):
        return self.status == 'trial' and self.trial_ends_at and self.trial_ends_at > timezone.now()
    
    @property
    def days_remaining(self):
        if self.current_period_end:
            remaining = self.current_period_end - timezone.now()
            return max(0, remaining.days)
        return 0
    
    def cancel(self, immediate=False):
        if immediate:
            self.status = 'cancelled'
            self.ends_at = timezone.now()
        else:
            self.cancel_at_period_end = True
        self.save()


class Coupon(models.Model):
    """Cupons de desconto"""
    
    DISCOUNT_TYPES = [
        ('percentage', 'Porcentagem'),
        ('fixed', 'Valor Fixo'),
        ('free_trial', 'Teste Grátis'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    
    # Discount
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Limits
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    max_uses_per_user = models.PositiveIntegerField(default=1)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # Applicable plans
    applicable_plans = models.ManyToManyField(SubscriptionPlan, blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    
    # Statistics
    times_used = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Cupom de Desconto'
        verbose_name_plural = 'Cupons de Desconto'
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}{'%' if self.discount_type == 'percentage' else ' R$'}"
    
    @property
    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.max_uses is None or self.times_used < self.max_uses)
        )


class CouponUsage(models.Model):
    """Registro de uso de cupons"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
    
    # Discount applied
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    original_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Uso de Cupom'
        verbose_name_plural = 'Usos de Cupons'
        unique_together = ['coupon', 'user', 'payment']
        ordering = ['-used_at']
    
    def __str__(self):
        return f"{self.user.email} usou {self.coupon.code} - R$ {self.discount_amount} de desconto"
