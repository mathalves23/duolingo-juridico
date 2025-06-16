from django.urls import path
from . import views

urlpatterns = [
    path('subscription-plans/', views.get_subscription_plans, name='subscription-plans'),
    path('create-payment/', views.create_payment, name='create-payment'),
    path('confirm-payment/', views.confirm_payment, name='confirm-payment'),
    path('subscription/', views.get_user_subscription, name='user-subscription'),
    path('cancel-subscription/', views.cancel_subscription, name='cancel-subscription'),
    path('payment-history/', views.get_payment_history, name='payment-history'),
] 