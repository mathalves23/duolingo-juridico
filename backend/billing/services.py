from typing import Dict, Any, Optional
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import stripe
import requests
import logging

from .models import Payment, Subscription, SubscriptionPlan, PaymentProvider, Coupon
from accounts.models import User

logger = logging.getLogger(__name__)

class PaymentService:
    """Serviço para processamento de pagamentos"""
    
    def __init__(self):
        self.stripe_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_...')
        stripe.api_key = self.stripe_key
    
    def create_payment_intent(self, amount: Decimal, currency: str = 'BRL', 
                            metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Cria um payment intent no Stripe"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe usa centavos
                currency=currency.lower(),
                metadata=metadata or {}
            )
            return {
                'success': True,
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }
        except Exception as e:
            logger.error(f"Erro ao criar payment intent: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_payment(self, user: User, plan: SubscriptionPlan, 
                       payment_method: str, coupon: Optional[Coupon] = None) -> Dict[str, Any]:
        """Processa o pagamento de uma assinatura"""
        try:
            # Calcula o valor final com desconto se houver cupom
            final_amount = plan.price
            if coupon and coupon.is_valid():
                if coupon.discount_type == 'percentage':
                    final_amount = plan.price * (1 - coupon.discount_value / 100)
                else:
                    final_amount = max(0, plan.price - coupon.discount_value)
            
            # Cria o pagamento no banco
            payment = Payment.objects.create(
                user=user,
                subscription_plan=plan,
                amount=final_amount,
                currency='BRL',
                payment_method=payment_method,
                status='pending',
                coupon=coupon
            )
            
            # Processa no gateway de pagamento
            if payment_method == 'stripe':
                result = self._process_stripe_payment(payment)
            elif payment_method == 'pagarme':
                result = self._process_pagarme_payment(payment)
            else:
                result = {'success': False, 'error': 'Método de pagamento não suportado'}
            
            # Atualiza o status do pagamento
            if result['success']:
                payment.status = 'completed'
                payment.gateway_transaction_id = result.get('transaction_id')
            else:
                payment.status = 'failed'
                payment.failure_reason = result.get('error')
            
            payment.save()
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao processar pagamento: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_stripe_payment(self, payment: Payment) -> Dict[str, Any]:
        """Processa pagamento via Stripe"""
        try:
            # Implementação do Stripe
            return {'success': True, 'transaction_id': 'stripe_' + str(payment.id)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _process_pagarme_payment(self, payment: Payment) -> Dict[str, Any]:
        """Processa pagamento via PagarMe"""
        try:
            # Implementação do PagarMe
            return {'success': True, 'transaction_id': 'pagarme_' + str(payment.id)}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class SubscriptionService:
    """Serviço para gerenciamento de assinaturas"""
    
    def create_subscription(self, user: User, plan: SubscriptionPlan, 
                          payment: Payment) -> Subscription:
        """Cria uma nova assinatura para o usuário"""
        
        # Calcula as datas
        start_date = timezone.now()
        
        if plan.trial_period_days > 0:
            trial_end_date = start_date + timedelta(days=plan.trial_period_days)
        else:
            trial_end_date = start_date
        
        if plan.billing_cycle == 'monthly':
            next_billing_date = trial_end_date + timedelta(days=30)
        elif plan.billing_cycle == 'yearly':
            next_billing_date = trial_end_date + timedelta(days=365)
        else:
            next_billing_date = None  # Para planos únicos
        
        # Cancela assinatura ativa se existir
        active_subscription = Subscription.objects.filter(
            user=user, 
            status='active'
        ).first()
        
        if active_subscription:
            active_subscription.status = 'cancelled'
            active_subscription.cancelled_at = timezone.now()
            active_subscription.save()
        
        # Cria a nova assinatura
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            payment=payment,
            status='active',
            start_date=start_date,
            trial_end_date=trial_end_date,
            next_billing_date=next_billing_date,
            current_period_start=start_date,
            current_period_end=next_billing_date or trial_end_date
        )
        
        return subscription
    
    def cancel_subscription(self, subscription: Subscription, 
                          immediate: bool = False) -> Dict[str, Any]:
        """Cancela uma assinatura"""
        try:
            if immediate:
                subscription.status = 'cancelled'
                subscription.cancelled_at = timezone.now()
                subscription.end_date = timezone.now()
            else:
                subscription.status = 'pending_cancellation'
                subscription.cancel_at_period_end = True
            
            subscription.save()
            
            return {'success': True, 'message': 'Assinatura cancelada com sucesso'}
            
        except Exception as e:
            logger.error(f"Erro ao cancelar assinatura: {e}")
            return {'success': False, 'error': str(e)}
    
    def renew_subscription(self, subscription: Subscription) -> Dict[str, Any]:
        """Renova uma assinatura"""
        try:
            # Processa o pagamento de renovação
            payment_service = PaymentService()
            payment_result = payment_service.process_payment(
                user=subscription.user,
                plan=subscription.plan,
                payment_method='stripe'  # Usar método padrão
            )
            
            if payment_result['success']:
                # Atualiza as datas da assinatura
                if subscription.plan.billing_cycle == 'monthly':
                    subscription.current_period_start = subscription.current_period_end
                    subscription.current_period_end += timedelta(days=30)
                    subscription.next_billing_date += timedelta(days=30)
                elif subscription.plan.billing_cycle == 'yearly':
                    subscription.current_period_start = subscription.current_period_end
                    subscription.current_period_end += timedelta(days=365)
                    subscription.next_billing_date += timedelta(days=365)
                
                subscription.save()
                
                return {'success': True, 'message': 'Assinatura renovada com sucesso'}
            else:
                return payment_result
                
        except Exception as e:
            logger.error(f"Erro ao renovar assinatura: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_active_subscription(self, user: User) -> Optional[Subscription]:
        """Retorna a assinatura ativa do usuário"""
        return Subscription.objects.filter(
            user=user,
            status='active'
        ).first()
    
    def check_subscription_access(self, user: User, feature: str) -> bool:
        """Verifica se o usuário tem acesso a uma funcionalidade"""
        subscription = self.get_user_active_subscription(user)
        
        if not subscription:
            return False
        
        plan_features = subscription.plan.features
        return feature in plan_features if plan_features else False


class CouponService:
    """Serviço para gerenciamento de cupons"""
    
    def validate_coupon(self, code: str, user: User = None) -> Dict[str, Any]:
        """Valida um cupom"""
        try:
            coupon = Coupon.objects.get(code=code)
            
            if not coupon.is_valid():
                return {'valid': False, 'error': 'Cupom inválido ou expirado'}
            
            if user and coupon.user_limit:
                usage_count = coupon.couponusage_set.filter(user=user).count()
                if usage_count >= coupon.user_limit:
                    return {'valid': False, 'error': 'Limite de uso do cupom excedido'}
            
            return {
                'valid': True,
                'coupon': coupon,
                'discount_type': coupon.discount_type,
                'discount_value': coupon.discount_value
            }
            
        except Coupon.DoesNotExist:
            return {'valid': False, 'error': 'Cupom não encontrado'}
        except Exception as e:
            logger.error(f"Erro ao validar cupom: {e}")
            return {'valid': False, 'error': str(e)}
    
    def apply_coupon(self, coupon: Coupon, user: User) -> Dict[str, Any]:
        """Aplica um cupom para um usuário"""
        try:
            # Registra o uso do cupom
            from .models import CouponUsage
            usage = CouponUsage.objects.create(
                coupon=coupon,
                user=user,
                used_at=timezone.now()
            )
            
            # Incrementa o contador de uso
            coupon.times_used += 1
            coupon.save()
            
            return {'success': True, 'usage': usage}
            
        except Exception as e:
            logger.error(f"Erro ao aplicar cupom: {e}")
            return {'success': False, 'error': str(e)} 