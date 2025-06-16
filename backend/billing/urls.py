"""
URLs para sistema de billing
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubscriptionPlanViewSet,
    PaymentViewSet,
    SubscriptionViewSet,
    CouponViewSet,
    PaymentWebhookView,
    CreatePaymentIntentView,
    ValidateCouponView
)

router = DefaultRouter()
router.register(r'plans', SubscriptionPlanViewSet)
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'coupons', CouponViewSet, basename='coupon')

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('validate-coupon/', ValidateCouponView.as_view(), name='validate-coupon'),
] 