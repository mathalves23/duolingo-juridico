"""
Views do sistema de assinatura premium
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import uuid
import secrets
from datetime import timedelta

from core.models import SubscriptionPlan, Payment, Subscription, UserProfile
from .serializers import (
    SubscriptionPlanSerializer, PaymentSerializer, 
    SubscriptionSerializer, PaymentCreateSerializer
)


class SubscriptionPlanListView(generics.ListAPIView):
    """Listar planos de assinatura disponíveis"""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    """Criar pagamento para assinatura"""
    serializer = PaymentCreateSerializer(data=request.data)
    if serializer.is_valid():
        plan_id = serializer.validated_data['subscription_plan_id']
        payment_method = serializer.validated_data['payment_method']
        billing_period = serializer.validated_data['billing_period']
        
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Plano não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # Calcular valor baseado no período
        amount = plan.price_monthly if billing_period == 'monthly' else plan.price_yearly
        
        # Criar pagamento
        payment = Payment.objects.create(
            user=request.user,
            subscription_plan=plan,
            payment_method=payment_method,
            amount=amount,
            billing_period=billing_period,
            transaction_id=f"TXN_{uuid.uuid4().hex[:12].upper()}",
            status='pending'
        )
        
        # Simular resposta do gateway de pagamento
        gateway_response = {}
        
        if payment_method == 'pix':
            gateway_response = {
                'qr_code': f"00020126580014BR.GOV.BCB.PIX{secrets.token_hex(32)}",
                'expires_in': 1800,  # 30 minutos
                'amount': str(amount)
            }
        elif payment_method in ['credit_card', 'debit_card']:
            gateway_response = {
                'redirect_url': f"https://gateway.exemplo.com/payment/{payment.transaction_id}",
                'expires_in': 3600,  # 1 hora
                'amount': str(amount)
            }
        elif payment_method == 'boleto':
            gateway_response = {
                'barcode': f"34191790010104351004791020150008291070026000",
                'due_date': (timezone.now() + timedelta(days=3)).isoformat(),
                'amount': str(amount)
            }
        
        payment.gateway_response = gateway_response
        payment.expires_at = timezone.now() + timedelta(seconds=gateway_response.get('expires_in', 3600))
        payment.save()
        
        return Response({
            'payment_id': payment.id,
            'transaction_id': payment.transaction_id,
            'amount': payment.amount,
            'status': payment.status,
            'gateway_response': gateway_response
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment(request, payment_id):
    """Confirmar pagamento e ativar assinatura"""
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
    except Payment.DoesNotExist:
        return Response({'error': 'Pagamento não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    if payment.status != 'pending':
        return Response({'error': 'Pagamento já processado'}, status=status.HTTP_400_BAD_REQUEST)
    
    with transaction.atomic():
        # Atualizar status do pagamento
        payment.status = 'completed'
        payment.paid_at = timezone.now()
        payment.save()
        
        # Criar ou atualizar assinatura
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            defaults={
                'subscription_plan': payment.subscription_plan,
                'billing_period': payment.billing_period,
                'status': 'active',
                'current_period_start': timezone.now(),
                'current_period_end': timezone.now() + timedelta(
                    days=30 if payment.billing_period == 'monthly' else 365
                )
            }
        )
        
        if not created:
            # Atualizar assinatura existente
            subscription.subscription_plan = payment.subscription_plan
            subscription.billing_period = payment.billing_period
            subscription.status = 'active'
            subscription.current_period_start = timezone.now()
            subscription.current_period_end = timezone.now() + timedelta(
                days=30 if payment.billing_period == 'monthly' else 365
            )
            subscription.save()
        
        # Atualizar perfil do usuário
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.subscription_type = payment.subscription_plan.plan_type
        profile.subscription_expires = subscription.current_period_end
        profile.save()
    
    return Response({
        'message': 'Pagamento confirmado e assinatura ativada',
        'subscription': SubscriptionSerializer(subscription).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """Cancelar assinatura"""
    try:
        subscription = Subscription.objects.get(user=request.user)
    except Subscription.DoesNotExist:
        return Response({'error': 'Assinatura não encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    cancel_immediately = request.data.get('cancel_immediately', False)
    
    if cancel_immediately:
        subscription.status = 'cancelled'
        subscription.cancelled_at = timezone.now()
        
        # Atualizar perfil
        profile = UserProfile.objects.get(user=request.user)
        profile.subscription_type = 'free'
        profile.subscription_expires = None
        profile.save()
    else:
        subscription.cancel_at_period_end = True
    
    subscription.save()
    
    return Response({
        'message': 'Assinatura cancelada com sucesso',
        'subscription': SubscriptionSerializer(subscription).data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    """Histórico de pagamentos do usuário"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_subscription(request):
    """Obter assinatura atual do usuário"""
    try:
        subscription = Subscription.objects.get(user=request.user)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)
    except Subscription.DoesNotExist:
        return Response({'error': 'Usuário não possui assinatura ativa'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscription_status(request):
    """Status detalhado da assinatura"""
    try:
        subscription = Subscription.objects.get(user=request.user)
        profile = UserProfile.objects.get(user=request.user)
        
        return Response({
            'has_subscription': True,
            'plan_name': subscription.subscription_plan.name,
            'plan_type': subscription.subscription_plan.plan_type,
            'status': subscription.status,
            'billing_period': subscription.billing_period,
            'current_period_end': subscription.current_period_end,
            'days_remaining': subscription.days_remaining(),
            'cancel_at_period_end': subscription.cancel_at_period_end,
            'is_active': subscription.is_active(),
            'features': subscription.subscription_plan.features,
            'limits': {
                'max_questions_per_day': subscription.subscription_plan.max_questions_per_day,
                'max_quizzes_per_day': subscription.subscription_plan.max_quizzes_per_day,
                'ai_explanations': subscription.subscription_plan.ai_explanations,
                'advanced_analytics': subscription.subscription_plan.advanced_analytics,
                'priority_support': subscription.subscription_plan.priority_support,
            }
        }, status=status.HTTP_200_OK)
    except Subscription.DoesNotExist:
        return Response({
            'has_subscription': False,
            'plan_name': 'Gratuito',
            'plan_type': 'free',
            'status': 'free',
            'limits': {
                'max_questions_per_day': 10,
                'max_quizzes_per_day': 1,
                'ai_explanations': False,
                'advanced_analytics': False,
                'priority_support': False,
            }
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def webhook_payment(request):
    """Webhook para confirmação de pagamentos do gateway"""
    # Simular webhook de confirmação
    transaction_id = request.data.get('transaction_id')
    status_payment = request.data.get('status')
    
    if not transaction_id or not status_payment:
        return Response({'error': 'Dados inválidos'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        payment = Payment.objects.get(transaction_id=transaction_id)
        
        if status_payment == 'approved':
            payment.status = 'completed'
            payment.paid_at = timezone.now()
            
            # Ativar assinatura (mesmo código do confirm_payment)
            with transaction.atomic():
                subscription, created = Subscription.objects.get_or_create(
                    user=payment.user,
                    defaults={
                        'subscription_plan': payment.subscription_plan,
                        'billing_period': payment.billing_period,
                        'status': 'active',
                        'current_period_start': timezone.now(),
                        'current_period_end': timezone.now() + timedelta(
                            days=30 if payment.billing_period == 'monthly' else 365
                        )
                    }
                )
                
                profile, _ = UserProfile.objects.get_or_create(user=payment.user)
                profile.subscription_type = payment.subscription_plan.plan_type
                profile.subscription_expires = subscription.current_period_end
                profile.save()
        
        elif status_payment in ['rejected', 'cancelled']:
            payment.status = 'failed'
        
        payment.save()
        
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
    
    except Payment.DoesNotExist:
        return Response({'error': 'Pagamento não encontrado'}, status=status.HTTP_404_NOT_FOUND) 