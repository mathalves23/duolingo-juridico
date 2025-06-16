from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
import uuid
import json

from core.models import SubscriptionPlan, Payment, Subscription, UserProfile, Notification

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_plans(request):
    """Retorna todos os planos de assinatura disponíveis"""
    plans = SubscriptionPlan.objects.filter(is_active=True)
    
    plans_data = []
    for plan in plans:
        plans_data.append({
            'id': plan.id,
            'name': plan.name,
            'plan_type': plan.plan_type,
            'price': float(plan.price),
            'duration_days': plan.duration_days,
            'features': plan.features,
            'is_popular': plan.plan_type == 'premium',
            'discount_percentage': 20 if plan.plan_type == 'plus' else 0
        })
    
    return Response({
        'plans': plans_data,
        'current_subscription': get_user_subscription_status(request.user)
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    """Cria um novo pagamento para assinatura"""
    plan_id = request.data.get('plan_id')
    payment_method = request.data.get('payment_method')
    
    if not plan_id or not payment_method:
        return Response({
            'error': 'Plan ID e método de pagamento são obrigatórios'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
    except SubscriptionPlan.DoesNotExist:
        return Response({
            'error': 'Plano não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Cria o pagamento
    transaction_id = str(uuid.uuid4())
    payment = Payment.objects.create(
        user=request.user,
        subscription_plan=plan,
        amount=plan.price,
        payment_method=payment_method,
        transaction_id=transaction_id,
        status='pending'
    )
    
    # Simula processamento do gateway
    payment_data = process_payment_gateway(payment)
    
    return Response({
        'payment_id': payment.id,
        'transaction_id': transaction_id,
        'status': payment.status,
        'payment_data': payment_data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment(request):
    """Confirma um pagamento e ativa a assinatura"""
    payment_id = request.data.get('payment_id')
    
    if not payment_id:
        return Response({
            'error': 'Payment ID é obrigatório'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
    except Payment.DoesNotExist:
        return Response({
            'error': 'Pagamento não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if payment.status != 'pending':
        return Response({
            'error': 'Pagamento já processado'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Simula confirmação do pagamento
    payment.status = 'approved'
    payment.gateway_response = {
        'confirmed_at': timezone.now().isoformat(),
        'method': payment.payment_method
    }
    payment.save()
    
    # Cria a assinatura
    starts_at = timezone.now()
    expires_at = starts_at + timedelta(days=payment.subscription_plan.duration_days)
    
    subscription = Subscription.objects.create(
        user=request.user,
        plan=payment.subscription_plan,
        payment=payment,
        starts_at=starts_at,
        expires_at=expires_at
    )
    
    # Atualiza o perfil do usuário
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    profile.subscription_type = payment.subscription_plan.plan_type
    profile.subscription_expires = expires_at
    profile.save()
    
    # Cria notificação
    Notification.objects.create(
        user=request.user,
        title="🎉 Assinatura Ativada!",
        message=f"Sua assinatura {payment.subscription_plan.name} foi ativada com sucesso!",
        notification_type='payment'
    )
    
    return Response({
        'message': 'Pagamento confirmado e assinatura ativada',
        'subscription': {
            'id': subscription.id,
            'plan': payment.subscription_plan.name,
            'expires_at': expires_at.isoformat()
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_subscription(request):
    """Retorna informações da assinatura atual do usuário"""
    subscription_data = get_user_subscription_status(request.user)
    return Response(subscription_data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """Cancela a assinatura do usuário"""
    try:
        subscription = Subscription.objects.get(
            user=request.user,
            is_active=True
        )
    except Subscription.DoesNotExist:
        return Response({
            'error': 'Nenhuma assinatura ativa encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    subscription.is_active = False
    subscription.auto_renew = False
    subscription.save()
    
    # Cria notificação
    Notification.objects.create(
        user=request.user,
        title="Assinatura Cancelada",
        message="Sua assinatura foi cancelada. Você terá acesso até o fim do período já pago.",
        notification_type='payment'
    )
    
    return Response({
        'message': 'Assinatura cancelada com sucesso',
        'expires_at': subscription.expires_at.isoformat()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_history(request):
    """Retorna histórico de pagamentos do usuário"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    payment_history = []
    for payment in payments:
        payment_history.append({
            'id': payment.id,
            'plan': payment.subscription_plan.name,
            'amount': float(payment.amount),
            'method': payment.get_payment_method_display(),
            'status': payment.get_status_display(),
            'created_at': payment.created_at.isoformat(),
            'transaction_id': payment.transaction_id
        })
    
    return Response({'payments': payment_history})

def get_user_subscription_status(user):
    """Função auxiliar para obter status da assinatura"""
    try:
        profile = UserProfile.objects.get(user=user)
        
        if profile.is_premium:
            subscription = Subscription.objects.filter(
                user=user,
                is_active=True
            ).first()
            
            return {
                'is_premium': True,
                'subscription_type': profile.subscription_type,
                'expires_at': profile.subscription_expires.isoformat(),
                'plan_name': subscription.plan.name if subscription else 'Unknown',
                'auto_renew': subscription.auto_renew if subscription else False
            }
    except UserProfile.DoesNotExist:
        pass
    
    return {
        'is_premium': False,
        'subscription_type': 'free',
        'expires_at': None,
        'plan_name': 'Grátis',
        'auto_renew': False
    }

def process_payment_gateway(payment):
    """Simula processamento no gateway de pagamento"""
    if payment.payment_method == 'pix':
        return {
            'type': 'pix',
            'qr_code': f'00020126580014BR.GOV.BCB.PIX0136{payment.transaction_id}520400005303986540{payment.amount}5802BR6009SAO_PAULO62070503***63041234',
            'pix_key': 'duolingo.juridico@email.com',
            'expires_in': 1800  # 30 minutos
        }
    elif payment.payment_method == 'boleto':
        return {
            'type': 'boleto',
            'barcode': '03399999999999999999999999999999999999999999',
            'due_date': (timezone.now() + timedelta(days=3)).isoformat(),
            'pdf_url': f'/api/payments/{payment.id}/boleto.pdf'
        }
    else:  # credit_card
        return {
            'type': 'credit_card',
            'redirect_url': f'/payment/card/{payment.transaction_id}',
            'requires_3ds': True
        } 