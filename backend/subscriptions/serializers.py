"""
Serializers do sistema de assinatura
"""

from rest_framework import serializers
from core.models import SubscriptionPlan, Payment, Subscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer para planos de assinatura"""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'plan_type', 'description', 'price_monthly', 'price_yearly',
            'features', 'max_questions_per_day', 'max_quizzes_per_day',
            'ai_explanations', 'advanced_analytics', 'priority_support'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer para pagamentos"""
    subscription_plan_name = serializers.CharField(source='subscription_plan.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'subscription_plan', 'subscription_plan_name', 'payment_method',
            'amount', 'currency', 'billing_period', 'status', 'transaction_id',
            'paid_at', 'created_at'
        ]
        read_only_fields = ['id', 'transaction_id', 'paid_at', 'created_at']


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer para criação de pagamento"""
    subscription_plan_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHODS)
    billing_period = serializers.ChoiceField(choices=[('monthly', 'Mensal'), ('yearly', 'Anual')])


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer para assinaturas"""
    subscription_plan = SubscriptionPlanSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'subscription_plan', 'status', 'billing_period',
            'current_period_start', 'current_period_end', 'cancel_at_period_end',
            'cancelled_at', 'trial_end', 'is_active', 'days_remaining',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 