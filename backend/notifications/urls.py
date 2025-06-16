from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserNotificationSettingsViewSet,
    DeviceTokenViewSet,
    NotificationViewSet,
    NotificationTemplateViewSet,
    NotificationAnalyticsView,
    SendTestNotificationView,
    BulkNotificationView
)
from . import views

router = DefaultRouter()
router.register(r'settings', UserNotificationSettingsViewSet, basename='notification-settings')
router.register(r'devices', DeviceTokenViewSet, basename='device-tokens')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'templates', NotificationTemplateViewSet, basename='notification-templates')

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/', NotificationAnalyticsView.as_view(), name='notification-analytics'),
    path('send-test/', SendTestNotificationView.as_view(), name='send-test-notification'),
    path('bulk-send/', BulkNotificationView.as_view(), name='bulk-notification'),
    path('', views.get_notifications, name='get-notifications'),
    path('mark-read/', views.mark_as_read, name='mark-as-read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark-all-as-read'),
    path('settings/', views.get_notification_settings, name='notification-settings'),
    path('settings/update/', views.update_notification_settings, name='update-notification-settings'),
    path('test/', views.send_test_notification, name='test-notification'),
    path('study-reminder/', views.create_study_reminder, name='study-reminder'),
    path('daily-summary/', views.get_daily_summary, name='daily-summary'),
    path('achievement/', views.send_achievement_notification, name='achievement-notification'),
    path('streak/', views.send_streak_notification, name='streak-notification'),
    path('<int:notification_id>/delete/', views.delete_notification, name='delete-notification'),
    path('clear-all/', views.clear_all_notifications, name='clear-all-notifications'),
] 