"""
Views para autenticação e gestão de usuários
"""

from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
import json
import csv
import io

from .models import User, UserProfile, UserActivity, LGPDConsent
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    ChangePasswordSerializer, UserStatsSerializer, UserActivitySerializer,
    LGPDConsentSerializer, DataExportSerializer, UserViewSetSerializer,
    UserProfileViewSetSerializer
)


class RegisterView(generics.CreateAPIView):
    """View para registro de usuários"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            user = serializer.save()
            
            # Registrar atividade
            UserActivity.objects.create(
                user=user,
                activity_type='login',
                description='Conta criada com sucesso',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Gerar tokens JWT
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LoginView(generics.CreateAPIView):
    """View para login de usuários"""
    
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Criar perfil se não existir
        if not hasattr(user, 'profile'):
            from .models import UserProfile
            UserProfile.objects.create(user=user)
        
        # Atualizar perfil
        profile = user.profile
        profile.login_count += 1
        profile.last_login_ip = self.get_client_ip(request)
        profile.save()
        
        # Registrar atividade
        UserActivity.objects.create(
            user=user,
            activity_type='login',
            description='Login realizado com sucesso',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Gerar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(generics.CreateAPIView):
    """View para logout de usuários"""
    
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Registrar atividade
            UserActivity.objects.create(
                user=request.user,
                activity_type='logout',
                description='Logout realizado',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View para visualizar e editar perfil do usuário"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """View para mudança de senha"""
    
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Verificar senha atual
            if not user.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Senha atual incorreta."]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Alterar senha
            user.set_password(serializer.data.get("new_password"))
            user.save()
            
            # Registrar atividade
            UserActivity.objects.create(
                user=user,
                activity_type='login',
                description='Senha alterada',
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return Response({'message': 'Senha alterada com sucesso.'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DeleteAccountView(generics.DestroyAPIView):
    """View para exclusão de conta (LGPD)"""
    
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        
        # Registrar atividade de exclusão
        UserActivity.objects.create(
            user=user,
            activity_type='data_deletion',
            description='Conta excluída pelo usuário',
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Anonimizar dados em vez de deletar (para manter integridade referencial)
        user.email = f"deleted_{user.id}@deleted.com"
        user.username = f"deleted_{user.id}"
        user.first_name = "Usuário"
        user.last_name = "Removido"
        user.is_active = False
        user.save()
        
        return Response({'message': 'Conta excluída com sucesso.'})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserStatsView(generics.RetrieveAPIView):
    """View para estatísticas do usuário"""
    
    serializer_class = UserStatsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class DataExportView(generics.CreateAPIView):
    """View para exportação de dados (LGPD)"""
    
    serializer_class = DataExportSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        export_format = serializer.validated_data.get('format', 'json')
        
        # Coletar dados do usuário
        user_data = {}
        
        if serializer.validated_data.get('include_profile', True):
            user_data['profile'] = UserProfileSerializer(user).data
        
        if serializer.validated_data.get('include_activities', True):
            activities = user.activities.all()[:100]  # Últimas 100 atividades
            user_data['activities'] = UserActivitySerializer(activities, many=True).data
        
        if serializer.validated_data.get('include_progress', True):
            user_data['progress'] = {
                'lessons_completed': user.user_lessons.filter(completed=True).count(),
                'quizzes_completed': user.quiz_attempts.filter(status='completed').count(),
                'achievements': user.achievements.count(),
            }
        
        # Registrar atividade de exportação
        UserActivity.objects.create(
            user=user,
            activity_type='data_export',
            description='Dados exportados pelo usuário',
            metadata={'format': export_format},
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Gerar arquivo de exportação
        if export_format == 'json':
            response = HttpResponse(
                json.dumps(user_data, indent=2, ensure_ascii=False, default=str),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="dados_usuario_{user.id}.json"'
        else:  # CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Dados básicos do perfil
            if 'profile' in user_data:
                writer.writerow(['Campo', 'Valor'])
                for key, value in user_data['profile'].items():
                    writer.writerow([key, value])
            
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="dados_usuario_{user.id}.csv"'
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LGPDConsentView(generics.CreateAPIView):
    """View para registrar consentimentos LGPD"""
    
    serializer_class = LGPDConsentSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Criar ou atualizar consentimento
        consent, created = LGPDConsent.objects.update_or_create(
            user=request.user,
            consent_type=serializer.validated_data['consent_type'],
            terms_version=serializer.validated_data.get('terms_version', '1.0'),
            defaults={
                'granted': serializer.validated_data['granted'],
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
        )
        
        return Response(
            LGPDConsentSerializer(consent).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# ViewSets para CRUD completo
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para usuários (apenas leitura)"""
    
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserViewSetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por nível de verificação se necessário
        if self.request.query_params.get('verified_only'):
            queryset = queryset.filter(is_verified=True)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        """Seguir outro usuário (funcionalidade social futura)"""
        target_user = self.get_object()
        if target_user == request.user:
            return Response(
                {'error': 'Você não pode seguir a si mesmo.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Implementar lógica de seguir
        return Response({'message': f'Seguindo {target_user.username}.'})


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet para perfis de usuário"""
    
    serializer_class = UserProfileViewSetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para atividades do usuário"""
    
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user).order_by('-created_at')


class LGPDConsentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para consentimentos LGPD"""
    
    serializer_class = LGPDConsentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LGPDConsent.objects.filter(user=self.request.user).order_by('-granted_at')
