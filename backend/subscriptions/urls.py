"""
URLs do sistema de assinatura
"""

from django.urls import path
from . import views

urlpatterns = [
    path('plans/', views.SubscriptionPlanListView.as_view(), name='subscription-plans'),
    path('create-payment/', views.create_payment, name='create-payment'),
    path('confirm-payment/<int:payment_id>/', views.confirm_payment, name='confirm-payment'),
    path('cancel/', views.cancel_subscription, name='cancel-subscription'),
    path('payment-history/', views.payment_history, name='payment-history'),
    path('current/', views.current_subscription, name='current-subscription'),
    path('status/', views.subscription_status, name='subscription-status'),
    path('webhook/', views.webhook_payment, name='webhook-payment'),
] 