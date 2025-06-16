"""
Views para sistema de pagamentos e assinaturas
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import logging
import requests

from .models import (
    PaymentProvider, SubscriptionPlan, Payment, 
    Subscription, Coupon, CouponUsage
)
from .serializers import (
    PaymentProviderSerializer, SubscriptionPlanSerializer,
    PaymentSerializer, SubscriptionSerializer, CouponSerializer
)

logger = logging.getLogger(__name__)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para planos de assinatura"""
    
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        plan_type = self.request.query_params.get('type')
        billing_cycle = self.request.query_params.get('billing_cycle')
        
        if plan_type:
            queryset = queryset.filter(plan_type=plan_type)
        if billing_cycle:
            queryset = queryset.filter(billing_cycle=billing_cycle)
            
        return queryset.order_by('sort_order', 'price')
    
    def list(self, request):
        """Listar planos disponíveis"""
        queryset = self.get_queryset()
        plans_data = []
        
        for plan in queryset:
            plan_data = {
                'id': str(plan.id),
                'name': plan.name,
                'plan_type': plan.plan_type,
                'description': plan.description,
                'price': float(plan.price),
                'original_price': float(plan.original_price) if plan.original_price else None,
                'billing_cycle': plan.billing_cycle,
                'max_questions_per_day': plan.max_questions_per_day,
                'max_simulations_per_month': plan.max_simulations_per_month,
                'has_ai_explanations': plan.has_ai_explanations,
                'has_study_plans': plan.has_study_plans,
                'has_progress_analytics': plan.has_progress_analytics,
                'has_offline_access': plan.has_offline_access,
                'has_priority_support': plan.has_priority_support,
                'has_custom_reminders': plan.has_custom_reminders,
                'is_featured': plan.is_featured,
                'has_trial': plan.has_trial,
                'trial_days': plan.trial_days,
                'discount_percentage': plan.discount_percentage
            }
            plans_data.append(plan_data)
        
        return Response(plans_data)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet para pagamentos"""
    
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Cria um novo pagamento"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Tenta novamente um pagamento que falhou"""
        payment = self.get_object()
        
        if payment.status != 'failed':
            return Response(
                {'error': 'Apenas pagamentos com falha podem ser repetidos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Aqui você implementaria a lógica de retry
        payment.status = 'pending'
        payment.save()
        
        return Response({'message': 'Pagamento reenviado para processamento'})


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet para assinaturas"""
    
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Cria uma nova assinatura"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Retorna a assinatura ativa do usuário"""
        subscription = Subscription.objects.filter(
            user=request.user,
            status='active'
        ).first()
        
        if subscription:
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        else:
            return Response({'message': 'Nenhuma assinatura ativa encontrada'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancela uma assinatura"""
        subscription = self.get_object()
        
        if subscription.status != 'active':
            return Response(
                {'error': 'Apenas assinaturas ativas podem ser canceladas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        immediate = request.data.get('immediate', False)
        
        if immediate:
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
            subscription.end_date = timezone.now()
        else:
            subscription.status = 'pending_cancellation'
            subscription.cancel_at_period_end = True
        
        subscription.save()
        
        return Response({'message': 'Assinatura cancelada com sucesso'})
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """Reativa uma assinatura cancelada"""
        subscription = self.get_object()
        
        if subscription.status not in ['cancelled', 'pending_cancellation']:
            return Response(
                {'error': 'Apenas assinaturas canceladas podem ser reativadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subscription.status = 'active'
        subscription.cancelled_at = None
        subscription.cancel_at_period_end = False
        subscription.save()
        
        return Response({'message': 'Assinatura reativada com sucesso'})


class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para cupons (apenas leitura para usuários)"""
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Coupon.objects.filter(is_active=True)
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Valida um cupom"""
        code = request.data.get('code')
        if not code:
            return Response(
                {'error': 'Código do cupom é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            coupon = Coupon.objects.get(code=code)
            
            if not coupon.is_valid():
                return Response(
                    {'valid': False, 'error': 'Cupom inválido ou expirado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verifica limite de uso por usuário
            if coupon.user_limit:
                usage_count = CouponUsage.objects.filter(
                    coupon=coupon, 
                    user=request.user
                ).count()
                
                if usage_count >= coupon.user_limit:
                    return Response(
                        {'valid': False, 'error': 'Limite de uso do cupom excedido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            serializer = self.get_serializer(coupon)
            return Response({
                'valid': True,
                'coupon': serializer.data
            })
            
        except Coupon.DoesNotExist:
            return Response(
                {'valid': False, 'error': 'Cupom não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


class PaymentWebhookView(APIView):
    """Endpoint para webhooks de pagamento"""
    permission_classes = []  # Webhooks não precisam de autenticação
    
    def post(self, request):
        """Processa webhooks de pagamento"""
        try:
            # Aqui você implementaria a lógica específica para cada provedor
            provider = request.data.get('provider', 'generic')
            
            if provider == 'stripe':
                return self._handle_stripe_webhook(request.data)
            elif provider == 'pagarme':
                return self._handle_pagarme_webhook(request.data)
            else:
                return Response(
                    {'error': 'Provedor não suportado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Erro no webhook de pagamento: {e}")
            return Response(
                {'error': 'Erro interno do servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _handle_stripe_webhook(self, data):
        """Processa webhook do Stripe"""
        # Implementar lógica específica do Stripe
        return Response({'status': 'processed'})
    
    def _handle_pagarme_webhook(self, data):
        """Processa webhook do PagarMe"""
        # Implementar lógica específica do PagarMe
        return Response({'status': 'processed'})


class CreatePaymentIntentView(APIView):
    """Cria um payment intent para pagamento"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Cria um payment intent"""
        try:
            plan_id = request.data.get('plan_id')
            coupon_code = request.data.get('coupon_code')
            
            if not plan_id:
                return Response(
                    {'error': 'Plan ID é obrigatório'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            plan = get_object_or_404(SubscriptionPlan, id=plan_id)
            
            # Calcula o valor final
            final_amount = plan.price
            coupon = None
            
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code)
                    if coupon.is_valid():
                        if coupon.discount_type == 'percentage':
                            final_amount = plan.price * (1 - coupon.discount_value / 100)
                        else:
                            final_amount = max(0, plan.price - coupon.discount_value)
                except Coupon.DoesNotExist:
                    pass
            
            # Cria o payment intent (simulado)
            return Response({
                'client_secret': f'pi_mock_{plan_id}_{request.user.id}',
                'amount': final_amount,
                'currency': 'BRL'
            })
            
        except Exception as e:
            logger.error(f"Erro ao criar payment intent: {e}")
            return Response(
                {'error': 'Erro interno do servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ValidateCouponView(APIView):
    """Valida um cupom de desconto"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Valida um cupom"""
        code = request.data.get('code')
        
        if not code:
            return Response(
                {'error': 'Código do cupom é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            coupon = Coupon.objects.get(code=code)
            
            if not coupon.is_valid():
                return Response({
                    'valid': False,
                    'error': 'Cupom inválido ou expirado'
                })
            
            # Verifica limite de uso por usuário
            if coupon.user_limit:
                usage_count = CouponUsage.objects.filter(
                    coupon=coupon,
                    user=request.user
                ).count()
                
                if usage_count >= coupon.user_limit:
                    return Response({
                        'valid': False,
                        'error': 'Limite de uso do cupom excedido'
                    })
            
            return Response({
                'valid': True,
                'discount_type': coupon.discount_type,
                'discount_value': coupon.discount_value,
                'description': coupon.description
            })
            
        except Coupon.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Cupom não encontrado'
            })
