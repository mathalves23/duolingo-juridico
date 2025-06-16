"""
URLs para autenticação e gestão de usuários
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'profiles', views.UserProfileViewSet, basename='userprofile')
router.register(r'activities', views.UserActivityViewSet, basename='useractivity')
router.register(r'lgpd-consents', views.LGPDConsentViewSet, basename='lgpdconsent')

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Profile management
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete-account'),
    
    # LGPD
    path('data-export/', views.DataExportView.as_view(), name='data-export'),
    path('lgpd-consent/', views.LGPDConsentView.as_view(), name='lgpd-consent'),
    
    # Statistics
    path('stats/', views.UserStatsView.as_view(), name='user-stats'),
    
    # Router URLs
    path('', include(router.urls)),
] 