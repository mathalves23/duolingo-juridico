"""
Serializers para sistema de pagamentos e assinaturas
"""

from rest_framework import serializers
from .models import (
    PaymentProvider, SubscriptionPlan, Payment, 
    Subscription, Coupon
)


class PaymentProviderSerializer(serializers.ModelSerializer):
    """Serializer para provedores de pagamento"""
    
    class Meta:
        model = PaymentProvider
        fields = [
            'id', 'name', 'display_name', 'is_active',
            'supports_pix', 'supports_boleto', 'supports_credit_card',
            'supports_installments', 'max_installments'
        ]


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer para planos de assinatura"""
    
    discount_percentage = serializers.ReadOnlyField()
    billing_cycle_display = serializers.CharField(source='get_billing_cycle_display', read_only=True)
    plan_type_display = serializers.CharField(source='get_plan_type_display', read_only=True)
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type', 'plan_type_display', 'description',
            'price', 'original_price', 'discount_percentage',
            'billing_cycle', 'billing_cycle_display',
            'max_questions_per_day', 'max_simulations_per_month',
            'has_ai_explanations', 'has_study_plans', 'has_progress_analytics',
            'has_offline_access', 'has_priority_support', 'has_custom_reminders',
            'is_featured', 'has_trial', 'trial_days'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer para pagamentos"""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    provider_name = serializers.CharField(source='provider.display_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user_email', 'plan_name', 'provider_name',
            'amount', 'currency', 'payment_method', 'payment_method_display',
            'installments', 'status', 'status_display',
            'created_at', 'paid_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at', 'paid_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer para assinaturas"""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active = serializers.ReadOnlyField()
    is_trial = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'user_email', 'plan_name', 'plan_details',
            'status', 'status_display', 'is_active', 'is_trial',
            'started_at', 'trial_ends_at', 'current_period_start',
            'current_period_end', 'ends_at', 'next_billing_date',
            'auto_renew', 'cancel_at_period_end', 'days_remaining'
        ]
        read_only_fields = ['id', 'started_at']


class CouponSerializer(serializers.ModelSerializer):
    """Serializer para cupons de desconto"""
    
    discount_type_display = serializers.CharField(source='get_discount_type_display', read_only=True)
    is_valid = serializers.ReadOnlyField()
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_type', 'discount_type_display',
            'discount_value', 'max_uses', 'max_uses_per_user', 'min_amount',
            'valid_from', 'valid_until', 'is_valid', 'times_used'
        ] 