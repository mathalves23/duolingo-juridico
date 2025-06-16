"""
Views para sistema de notificações
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
import json

from .models import (
    NotificationTemplate, UserNotificationSettings, 
    DeviceToken, Notification, NotificationSchedule
)
from core.models import NotificationPreference, UserProfile
from django.contrib.auth.models import User
from .serializers import NotificationSerializer, NotificationPreferenceSerializer, NotificationTemplateSerializer
from .tasks import send_push_notification, send_email_notification


class UserNotificationSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet para configurações de notificação do usuário"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserNotificationSettings.objects.filter(user=self.request.user)
    
    def get_object(self):
        obj, created = UserNotificationSettings.objects.get_or_create(
            user=self.request.user
        )
        return obj
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Obter configurações atuais do usuário"""
        settings = self.get_object()
        
        return Response({
            'push_notifications_enabled': settings.push_notifications_enabled,
            'email_notifications_enabled': settings.email_notifications_enabled,
            'sms_notifications_enabled': settings.sms_notifications_enabled,
            'study_reminders': settings.study_reminders,
            'achievement_notifications': settings.achievement_notifications,
            'streak_reminders': settings.streak_reminders,
            'simulation_notifications': settings.simulation_notifications,
            'content_notifications': settings.content_notifications,
            'subscription_notifications': settings.subscription_notifications,
            'social_notifications': settings.social_notifications,
            'notification_start_time': settings.notification_start_time.strftime('%H:%M'),
            'notification_end_time': settings.notification_end_time.strftime('%H:%M'),
            'daily_reminder_enabled': settings.daily_reminder_enabled,
            'weekly_report_enabled': settings.weekly_report_enabled
        })
    
    @action(detail=False, methods=['post'])
    def update_settings(self, request):
        """Atualizar configurações de notificação"""
        settings = self.get_object()
        
        # Atualizar campos fornecidos
        for field, value in request.data.items():
            if hasattr(settings, field):
                setattr(settings, field, value)
        
        settings.save()
        
        return Response({
            'message': 'Configurações atualizadas com sucesso'
        })


class DeviceTokenViewSet(viewsets.ModelViewSet):
    """ViewSet para tokens de dispositivos"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DeviceToken.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def register_device(self, request):
        """Registrar token de dispositivo"""
        token = request.data.get('token')
        device_type = request.data.get('device_type')
        device_id = request.data.get('device_id', '')
        
        if not token or not device_type:
            return Response({
                'error': 'Token e tipo de dispositivo são obrigatórios'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Desativar tokens antigos do mesmo dispositivo
        DeviceToken.objects.filter(
            user=request.user,
            device_id=device_id
        ).update(is_active=False)
        
        # Criar ou atualizar token
        device_token, created = DeviceToken.objects.get_or_create(
            user=request.user,
            token=token,
            defaults={
                'device_type': device_type,
                'device_id': device_id,
                'app_version': request.data.get('app_version', ''),
                'os_version': request.data.get('os_version', ''),
                'device_model': request.data.get('device_model', ''),
                'is_active': True
            }
        )
        
        if not created:
            device_token.is_active = True
            device_token.device_type = device_type
            device_token.device_id = device_id
            device_token.save()
        
        return Response({
            'message': 'Token registrado com sucesso',
            'device_id': str(device_token.id)
        })
    
    @action(detail=True, methods=['post'])
    def unregister_device(self, request, pk=None):
        """Desregistrar token de dispositivo"""
        device_token = self.get_object()
        device_token.is_active = False
        device_token.save()
        
        return Response({
            'message': 'Dispositivo desregistrado com sucesso'
        })


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para notificações do usuário"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    def list(self, request):
        """Listar notificações do usuário"""
        queryset = self.get_queryset()
        
        # Filtros
        status_filter = request.query_params.get('status')
        notification_type = request.query_params.get('type')
        unread_only = request.query_params.get('unread_only', 'false').lower() == 'true'
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        if unread_only:
            queryset = queryset.exclude(status='read')
        
        # Paginação simples
        page_size = 20
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        notifications = queryset[start:end]
        total_count = queryset.count()
        unread_count = queryset.exclude(status='read').count()
        
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'id': str(notification.id),
                'title': notification.title,
                'body': notification.body,
                'notification_type': notification.notification_type,
                'status': notification.status,
                'action_url': notification.action_url,
                'icon_url': notification.icon_url,
                'created_at': notification.created_at.isoformat(),
                'read_at': notification.read_at.isoformat() if notification.read_at else None
            })
        
        return Response({
            'notifications': notifications_data,
            'total_count': total_count,
            'unread_count': unread_count,
            'has_next': end < total_count,
            'page': page
        })
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Marcar notificação como lida"""
        notification = self.get_object()
        notification.mark_as_read()
        
        return Response({
            'message': 'Notificação marcada como lida'
        })
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Marcar todas as notificações como lidas"""
        count = Notification.objects.filter(
            user=request.user,
            status__in=['sent', 'delivered']
        ).update(
            status='read',
            read_at=timezone.now()
        )
        
        return Response({
            'message': f'{count} notificações marcadas como lidas'
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Obter contagem de notificações não lidas"""
        count = Notification.objects.filter(
            user=request.user
        ).exclude(status='read').count()
        
        return Response({
            'unread_count': count
        })


class NotificationService:
    """Serviço para envio de notificações"""
    
    @staticmethod
    def send_notification(user, notification_type, title, body, **kwargs):
        """Enviar notificação para um usuário"""
        
        # Verificar configurações do usuário
        try:
            settings = UserNotificationSettings.objects.get(user=user)
        except UserNotificationSettings.DoesNotExist:
            settings = UserNotificationSettings.objects.create(user=user)
        
        # Verificar se o tipo de notificação está habilitado
        type_enabled = getattr(settings, f"{notification_type}_notifications", True)
        if not type_enabled:
            return None
        
        # Criar notificação
        notification = Notification.objects.create(
            user=user,
            title=title,
            body=body,
            notification_type=notification_type,
            platform='push',
            action_url=kwargs.get('action_url', ''),
            icon_url=kwargs.get('icon_url', ''),
            image_url=kwargs.get('image_url', ''),
            metadata=kwargs.get('metadata', {})
        )
        
        # Enviar push notification se habilitado
        if settings.push_notifications_enabled:
            NotificationService._send_push_notification(user, notification)
        
        # Enviar email se habilitado
        if settings.email_notifications_enabled:
            NotificationService._send_email_notification(user, notification)
        
        return notification
    
    @staticmethod
    def _send_push_notification(user, notification):
        """Enviar push notification"""
        # Obter tokens ativos do usuário
        device_tokens = DeviceToken.objects.filter(
            user=user,
            is_active=True
        )
        
        for device_token in device_tokens:
            try:
                # Aqui seria a integração com Firebase FCM ou similar
                # Por enquanto, apenas marcar como enviada
                notification.mark_as_sent()
                print(f"Push enviado para {device_token.token[:20]}...")
            except Exception as e:
                print(f"Erro ao enviar push: {e}")
    
    @staticmethod
    def _send_email_notification(user, notification):
        """Enviar email de notificação"""
        try:
            # Aqui seria a integração com serviço de email
            # Por enquanto, apenas log
            print(f"Email enviado para {user.email}: {notification.title}")
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
    
    @staticmethod
    def send_study_reminder(user):
        """Enviar lembrete de estudo"""
        return NotificationService.send_notification(
            user=user,
            notification_type='study_reminder',
            title='⏰ Hora de estudar!',
            body='Que tal resolver algumas questões hoje? Sua sequência de estudos está esperando por você!',
            action_url='/questions'
        )
    
    @staticmethod
    def send_achievement_notification(user, achievement_name):
        """Enviar notificação de conquista"""
        return NotificationService.send_notification(
            user=user,
            notification_type='achievement_unlocked',
            title='🏆 Nova conquista desbloqueada!',
            body=f'Parabéns! Você conquistou: {achievement_name}',
            action_url='/achievements'
        )
    
    @staticmethod
    def send_streak_reminder(user, streak_days):
        """Enviar lembrete de sequência"""
        return NotificationService.send_notification(
            user=user,
            notification_type='streak_reminder',
            title='🔥 Mantenha sua sequência!',
            body=f'Você está com {streak_days} dias de sequência. Continue assim!',
            action_url='/questions'
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """Retorna todas as notificações do usuário"""
    notifications = Notification.objects.filter(user=request.user)[:20]
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'time_ago': get_time_ago(notification.created_at)
        })
    
    # Conta não lidas
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    return Response({
        'notifications': notifications_data,
        'unread_count': unread_count
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_read(request):
    """Marca notificação como lida"""
    notification_id = request.data.get('notification_id')
    
    if not notification_id:
        return Response({
            'error': 'Notification ID é obrigatório'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        
        return Response({'message': 'Notificação marcada como lida'})
    except Notification.DoesNotExist:
        return Response({
            'error': 'Notificação não encontrada'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_as_read(request):
    """Marca todas as notificações como lidas"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'Todas as notificações foram marcadas como lidas'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notification_settings(request):
    """Retorna configurações de notificação do usuário"""
    settings, created = NotificationSettings.objects.get_or_create(user=request.user)
    
    return Response({
        'email_notifications': settings.email_notifications,
        'push_notifications': settings.push_notifications,
        'study_reminders': settings.study_reminders,
        'achievement_alerts': settings.achievement_alerts,
        'social_notifications': settings.social_notifications
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_notification_settings(request):
    """Atualiza configurações de notificação"""
    settings, created = NotificationSettings.objects.get_or_create(user=request.user)
    
    settings.email_notifications = request.data.get('email_notifications', settings.email_notifications)
    settings.push_notifications = request.data.get('push_notifications', settings.push_notifications)
    settings.study_reminders = request.data.get('study_reminders', settings.study_reminders)
    settings.achievement_alerts = request.data.get('achievement_alerts', settings.achievement_alerts)
    settings.social_notifications = request.data.get('social_notifications', settings.social_notifications)
    
    settings.save()
    
    return Response({'message': 'Configurações atualizadas com sucesso'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_test_notification(request):
    """Envia notificação de teste"""
    Notification.objects.create(
        user=request.user,
        title="🧪 Notificação de Teste",
        message="Esta é uma notificação de teste para verificar se tudo está funcionando corretamente!",
        notification_type='system'
    )
    
    return Response({'message': 'Notificação de teste enviada'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_study_reminder(request):
    """Cria lembrete de estudo personalizado"""
    title = request.data.get('title', 'Hora de Estudar!')
    message = request.data.get('message', 'Não esqueça de fazer suas questões diárias!')
    reminder_time = request.data.get('reminder_time')  # Format: "14:30"
    
    if not reminder_time:
        return Response({
            'error': 'Horário do lembrete é obrigatório'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Cria notificação de lembrete
    Notification.objects.create(
        user=request.user,
        title=f"⏰ {title}",
        message=message,
        notification_type='study_reminder'
    )
    
    return Response({'message': 'Lembrete de estudo criado com sucesso'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_daily_summary(request):
    """Retorna resumo diário do usuário para notificações"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        
        # Simula estatísticas diárias
        today_stats = {
            'questions_answered': 15,
            'correct_percentage': 78,
            'xp_gained': 120,
            'streak': profile.streak,
            'study_time': 45,  # minutos
            'ranking_position': 5
        }
        
        # Cria notificação de resumo diário
        summary_message = f"""
📊 Seu resumo de hoje:
• {today_stats['questions_answered']} questões respondidas
• {today_stats['correct_percentage']}% de acertos
• {today_stats['xp_gained']} XP ganhos
• {today_stats['study_time']} minutos de estudo
• Posição #{today_stats['ranking_position']} no ranking
        """.strip()
        
        return Response({
            'summary': today_stats,
            'message': summary_message
        })
        
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Perfil não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_achievement_notification(request):
    """Envia notificação de conquista"""
    achievement_name = request.data.get('achievement_name', 'Nova Conquista!')
    achievement_description = request.data.get('achievement_description', 'Parabéns pela sua conquista!')
    
    Notification.objects.create(
        user=request.user,
        title=f"🏆 {achievement_name}",
        message=f"Parabéns! Você desbloqueou: {achievement_description}",
        notification_type='achievement'
    )
    
    return Response({'message': 'Notificação de conquista enviada'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_streak_notification(request):
    """Envia notificação de sequência de estudos"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        
        if profile.streak >= 7:
            title = f"🔥 {profile.streak} Dias Consecutivos!"
            message = f"Incrível! Você está com {profile.streak} dias consecutivos de estudo. Continue assim!"
        elif profile.streak >= 3:
            title = f"⚡ {profile.streak} Dias Seguidos!"
            message = f"Você está indo bem! {profile.streak} dias consecutivos de dedicação."
        else:
            title = "📚 Continue Estudando!"
            message = "Que tal manter a sequência? Faça pelo menos uma questão hoje!"
        
        Notification.objects.create(
            user=request.user,
            title=title,
            message=message,
            notification_type='study_reminder'
        )
        
        return Response({'message': 'Notificação de streak enviada'})
        
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Perfil não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    """Deleta uma notificação específica"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        return Response({'message': 'Notificação deletada com sucesso'})
    except Notification.DoesNotExist:
        return Response({
            'error': 'Notificação não encontrada'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_all_notifications(request):
    """Limpa todas as notificações do usuário"""
    deleted_count = Notification.objects.filter(user=request.user).count()
    Notification.objects.filter(user=request.user).delete()
    
    return Response({
        'message': f'{deleted_count} notificações foram removidas'
    })

def get_time_ago(created_at):
    """Calcula tempo relativo desde a criação"""
    now = timezone.now()
    diff = now - created_at
    
    if diff.days > 0:
        return f"{diff.days} dia{'s' if diff.days > 1 else ''} atrás"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hora{'s' if hours > 1 else ''} atrás"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minuto{'s' if minutes > 1 else ''} atrás"
    else:
        return "Agora mesmo"

# Funções auxiliares para notificações automáticas
def create_welcome_notification(user):
    """Cria notificação de boas-vindas para novos usuários"""
    Notification.objects.create(
        user=user,
        title="🎉 Bem-vindo ao Duolingo Jurídico!",
        message="Que tal começar fazendo algumas questões? Você ganha 100 moedas de bônus nas primeiras 24 horas!",
        notification_type='system'
    )

def create_daily_reminder_notifications():
    """Cria lembretes diários para usuários ativos"""
    # Esta função seria chamada por um cron job
    users_to_remind = User.objects.filter(
        notificationsettings__study_reminders=True,
        userprofile__last_activity__lt=timezone.now() - timedelta(hours=24)
    )
    
    for user in users_to_remind:
        Notification.objects.create(
            user=user,
            title="📚 Hora de Estudar!",
            message="Você não fez questões hoje. Que tal manter sua sequência de estudos?",
            notification_type='study_reminder'
        )

def create_weekly_progress_notification(user):
    """Cria notificação de progresso semanal"""
    try:
        profile = UserProfile.objects.get(user=user)
        
        # Simula dados semanais
        weekly_stats = {
            'questions_answered': 85,  # Esta semana
            'xp_gained': 650,
            'streak_maintained': 5,
            'achievements_unlocked': 2
        }
        
        message = f"""
📈 Seu progresso desta semana:
• {weekly_stats['questions_answered']} questões respondidas
• {weekly_stats['xp_gained']} XP conquistados
• {weekly_stats['streak_maintained']} dias de streak
• {weekly_stats['achievements_unlocked']} novas conquistas
        """.strip()
        
        Notification.objects.create(
            user=user,
            title="📊 Resumo Semanal",
            message=message,
            notification_type='system'
        )
        
    except UserProfile.DoesNotExist:
        pass

class NotificationListView(viewsets.ReadOnlyModelViewSet):
    """Listar notificações do usuário"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_read(request, notification_id):
    """Marcar notificação como lida"""
    try:
        notification = Notification.objects.get(
            id=notification_id, 
            recipient=request.user
        )
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return Response({
            'message': 'Notificação marcada como lida',
            'notification': NotificationSerializer(notification).data
        })
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notificação não encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_as_read(request):
    """Marcar todas as notificações como lidas"""
    updated_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return Response({
        'message': f'{updated_count} notificações marcadas como lidas'
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def notification_count(request):
    """Contar notificações não lidas"""
    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return Response({
        'unread_count': unread_count
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def notification_preferences(request):
    """Obter ou atualizar preferências de notificação"""
    preference, created = NotificationPreference.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'GET':
        serializer = NotificationPreferenceSerializer(preference)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = NotificationPreferenceSerializer(
            preference, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_test_notification(request):
    """Enviar notificação de teste"""
    user = request.user
    
    # Criar notificação de teste
    notification = Notification.objects.create(
        recipient=user,
        title="Notificação de Teste",
        message="Esta é uma notificação de teste para verificar se o sistema está funcionando.",
        notification_type="test",
        data={'test': True}
    )
    
    # Verificar preferências do usuário
    try:
        preferences = NotificationPreference.objects.get(user=user)
        
        if preferences.push_notifications:
            # Enviar push notification (simulado)
            send_push_notification.delay(
                user_id=user.id,
                title=notification.title,
                message=notification.message,
                data=notification.data
            )
        
        if preferences.email_notifications:
            # Enviar email notification (simulado)
            send_email_notification.delay(
                user_id=user.id,
                subject=notification.title,
                message=notification.message
            )
    
    except NotificationPreference.DoesNotExist:
        pass
    
    return Response({
        'message': 'Notificação de teste enviada',
        'notification': NotificationSerializer(notification).data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_reminder_notification(request):
    """Enviar lembrete de estudos"""
    user = request.user
    
    try:
        profile = UserProfile.objects.get(user=user)
        preferences = NotificationPreference.objects.get(user=user)
        
        if not preferences.streak_reminders:
            return Response({'message': 'Lembretes desabilitados pelo usuário'})
        
        # Verificar se já estudou hoje
        today = timezone.now().date()
        last_activity = profile.last_activity.date() if profile.last_activity else None
        
        if last_activity != today:
            # Criar notificação de lembrete
            notification = Notification.objects.create(
                recipient=user,
                title="Hora de Estudar! 📚",
                message=f"Mantenha sua sequência de {profile.streak} dias! Responda algumas questões hoje.",
                notification_type="reminder",
                data={
                    'streak': profile.streak,
                    'reminder_type': 'daily_study'
                }
            )
            
            if preferences.push_notifications:
                send_push_notification.delay(
                    user_id=user.id,
                    title=notification.title,
                    message=notification.message,
                    data=notification.data
                )
            
            return Response({
                'message': 'Lembrete enviado',
                'notification': NotificationSerializer(notification).data
            })
        else:
            return Response({'message': 'Usuário já estudou hoje'})
            
    except (UserProfile.DoesNotExist, NotificationPreference.DoesNotExist):
        return Response(
            {'error': 'Perfil ou preferências não encontradas'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_achievement_notification(request):
    """Enviar notificação de conquista"""
    user = request.user
    achievement_data = request.data
    
    try:
        preferences = NotificationPreference.objects.get(user=user)
        
        if not preferences.achievement_notifications:
            return Response({'message': 'Notificações de conquistas desabilitadas'})
        
        # Criar notificação de conquista
        notification = Notification.objects.create(
            recipient=user,
            title=f"🏆 Nova Conquista: {achievement_data.get('name', 'Conquista')}",
            message=achievement_data.get('description', 'Parabéns por sua nova conquista!'),
            notification_type="achievement",
            data={
                'achievement_id': achievement_data.get('id'),
                'achievement_name': achievement_data.get('name'),
                'points_earned': achievement_data.get('points', 0)
            }
        )
        
        if preferences.push_notifications:
            send_push_notification.delay(
                user_id=user.id,
                title=notification.title,
                message=notification.message,
                data=notification.data
            )
        
        return Response({
            'message': 'Notificação de conquista enviada',
            'notification': NotificationSerializer(notification).data
        })
        
    except NotificationPreference.DoesNotExist:
        return Response(
            {'error': 'Preferências não encontradas'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_streak_milestone_notification(request):
    """Enviar notificação de marco de sequência"""
    user = request.user
    streak_days = request.data.get('streak_days', 0)
    
    try:
        preferences = NotificationPreference.objects.get(user=user)
        
        if not preferences.streak_reminders:
            return Response({'message': 'Lembretes de sequência desabilitados'})
        
        # Mensagens especiais para marcos importantes
        milestone_messages = {
            7: "Uma semana completa! 🔥",
            14: "Duas semanas de dedicação! 💪",
            30: "Um mês incrível de estudos! 🌟",
            60: "Dois meses de consistência! 🚀",
            100: "100 dias! Você é imparável! 👑",
            365: "Um ano completo! Lendário! 🏆"
        }
        
        milestone_message = milestone_messages.get(
            streak_days, 
            f"{streak_days} dias consecutivos de estudos!"
        )
        
        # Criar notificação de marco
        notification = Notification.objects.create(
            recipient=user,
            title=f"🔥 {streak_days} Dias de Sequência!",
            message=milestone_message,
            notification_type="streak_milestone",
            data={
                'streak_days': streak_days,
                'milestone_type': 'streak'
            }
        )
        
        if preferences.push_notifications:
            send_push_notification.delay(
                user_id=user.id,
                title=notification.title,
                message=notification.message,
                data=notification.data
            )
        
        return Response({
            'message': 'Notificação de marco enviada',
            'notification': NotificationSerializer(notification).data
        })
        
    except NotificationPreference.DoesNotExist:
        return Response(
            {'error': 'Preferências não encontradas'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    """Deletar notificação"""
    try:
        notification = Notification.objects.get(
            id=notification_id, 
            recipient=request.user
        )
        notification.delete()
        
        return Response({'message': 'Notificação deletada'})
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notificação não encontrada'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_device_token(request):
    """Registrar token do dispositivo para push notifications"""
    device_token = request.data.get('device_token')
    device_type = request.data.get('device_type', 'mobile')  # mobile, web
    
    if not device_token:
        return Response(
            {'error': 'Token do dispositivo é obrigatório'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Salvar token no perfil do usuário (simulado)
    try:
        profile = UserProfile.objects.get(user=request.user)
        
        # Adicionar token aos metadados do perfil
        if not hasattr(profile, 'device_tokens'):
            profile.device_tokens = []
        
        # Remover token existente se houver
        profile.device_tokens = [
            token for token in profile.device_tokens 
            if token.get('token') != device_token
        ]
        
        # Adicionar novo token
        profile.device_tokens.append({
            'token': device_token,
            'device_type': device_type,
            'registered_at': timezone.now().isoformat()
        })
        
        profile.save()
        
        return Response({'message': 'Token registrado com sucesso'})
        
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'Perfil não encontrado'}, 
            status=status.HTTP_404_NOT_FOUND
        )
