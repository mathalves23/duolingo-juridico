from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta

from core.models import UserProfile, Notification
from django.contrib.auth.models import User
from .models import Friendship, Follow, UserActivity, SocialGroup, GroupMembership, ForumPost, ForumReply
from .serializers import UserSearchSerializer, UserProfileSerializer, UserActivitySerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    """Buscar usuários por nome ou email"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return Response({'error': 'Query deve ter pelo menos 2 caracteres'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Buscar usuários (excluindo o próprio usuário)
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(email__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id)[:20]  # Limite de 20 resultados
    
    serializer = UserSearchSerializer(users, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, user_id):
    """Seguir usuário"""
    try:
        user_to_follow = User.objects.get(id=user_id)
        
        if user_to_follow == request.user:
            return Response({'error': 'Você não pode seguir a si mesmo'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar se já está seguindo
        current_user_profile = UserProfile.objects.get(user=request.user)
        
        # Inicializar following se não existir
        if not hasattr(current_user_profile, 'following'):
            current_user_profile.following = []
        
        if user_id not in current_user_profile.following:
            current_user_profile.following.append(user_id)
            current_user_profile.save()
            
            # Adicionar aos seguidores do usuário alvo
            target_user_profile, _ = UserProfile.objects.get_or_create(user=user_to_follow)
            if not hasattr(target_user_profile, 'followers'):
                target_user_profile.followers = []
            
            if request.user.id not in target_user_profile.followers:
                target_user_profile.followers.append(request.user.id)
                target_user_profile.save()
            
            # Criar atividade social
            UserActivity.objects.create(
                user=request.user,
                activity_type='social_follow',
                description=f'Começou a seguir {user_to_follow.username}',
                metadata={'followed_user_id': user_id, 'followed_username': user_to_follow.username}
            )
            
            return Response({'message': f'Agora você está seguindo {user_to_follow.username}'})
        else:
            return Response({'message': 'Você já está seguindo este usuário'})
            
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, 
                       status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Perfil não encontrado'}, 
                       status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, user_id):
    """Deixar de seguir usuário"""
    try:
        user_to_unfollow = User.objects.get(id=user_id)
        current_user_profile = UserProfile.objects.get(user=request.user)
        
        # Remover dos seguindo
        if hasattr(current_user_profile, 'following') and user_id in current_user_profile.following:
            current_user_profile.following.remove(user_id)
            current_user_profile.save()
            
            # Remover dos seguidores do usuário alvo
            target_user_profile = UserProfile.objects.get(user=user_to_unfollow)
            if hasattr(target_user_profile, 'followers') and request.user.id in target_user_profile.followers:
                target_user_profile.followers.remove(request.user.id)
                target_user_profile.save()
            
            return Response({'message': f'Você deixou de seguir {user_to_unfollow.username}'})
        else:
            return Response({'message': 'Você não está seguindo este usuário'})
            
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, 
                       status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Perfil não encontrado'}, 
                       status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_friend_request(request, user_id):
    """Enviar solicitação de amizade"""
    try:
        user_to_befriend = User.objects.get(id=user_id)
        
        if user_to_befriend == request.user:
            return Response({'error': 'Você não pode enviar solicitação para si mesmo'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        current_user_profile = UserProfile.objects.get(user=request.user)
        target_user_profile, _ = UserProfile.objects.get_or_create(user=user_to_befriend)
        
        # Inicializar listas se não existirem
        if not hasattr(current_user_profile, 'friend_requests_sent'):
            current_user_profile.friend_requests_sent = []
        if not hasattr(target_user_profile, 'friend_requests_received'):
            target_user_profile.friend_requests_received = []
        
        # Verificar se já enviou solicitação
        if user_id not in current_user_profile.friend_requests_sent:
            current_user_profile.friend_requests_sent.append(user_id)
            current_user_profile.save()
            
            target_user_profile.friend_requests_received.append(request.user.id)
            target_user_profile.save()
            
            # Criar atividade social
            UserActivity.objects.create(
                user=request.user,
                activity_type='social_friend_request',
                description=f'Enviou solicitação de amizade para {user_to_befriend.username}',
                metadata={'target_user_id': user_id, 'target_username': user_to_befriend.username}
            )
            
            return Response({'message': f'Solicitação de amizade enviada para {user_to_befriend.username}'})
        else:
            return Response({'message': 'Solicitação já enviada'})
            
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, 
                       status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Perfil não encontrado'}, 
                       status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_friend_request(request, user_id):
    """Aceitar solicitação de amizade"""
    try:
        requester_user = User.objects.get(id=user_id)
        current_user_profile = UserProfile.objects.get(user=request.user)
        requester_profile = UserProfile.objects.get(user=requester_user)
        
        # Verificar se há solicitação pendente
        if (hasattr(current_user_profile, 'friend_requests_received') and 
            user_id in current_user_profile.friend_requests_received):
            
            # Remover das solicitações
            current_user_profile.friend_requests_received.remove(user_id)
            requester_profile.friend_requests_sent.remove(request.user.id)
            
            # Adicionar às listas de amigos
            if not hasattr(current_user_profile, 'friends'):
                current_user_profile.friends = []
            if not hasattr(requester_profile, 'friends'):
                requester_profile.friends = []
            
            current_user_profile.friends.append(user_id)
            requester_profile.friends.append(request.user.id)
            
            current_user_profile.save()
            requester_profile.save()
            
            # Criar atividade social
            UserActivity.objects.create(
                user=request.user,
                activity_type='social_friend_accepted',
                description=f'Aceitou solicitação de amizade de {requester_user.username}',
                metadata={'friend_user_id': user_id, 'friend_username': requester_user.username}
            )
            
            return Response({'message': f'Agora você e {requester_user.username} são amigos!'})
        else:
            return Response({'error': 'Solicitação de amizade não encontrada'}, 
                           status=status.HTTP_404_NOT_FOUND)
            
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, 
                       status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Perfil não encontrado'}, 
                       status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_friend_request(request, user_id):
    """Rejeitar solicitação de amizade"""
    try:
        requester_user = User.objects.get(id=user_id)
        current_user_profile = UserProfile.objects.get(user=request.user)
        requester_profile = UserProfile.objects.get(user=requester_user)
        
        # Verificar se há solicitação pendente
        if (hasattr(current_user_profile, 'friend_requests_received') and 
            user_id in current_user_profile.friend_requests_received):
            
            # Remover das solicitações
            current_user_profile.friend_requests_received.remove(user_id)
            requester_profile.friend_requests_sent.remove(request.user.id)
            
            current_user_profile.save()
            requester_profile.save()
            
            return Response({'message': 'Solicitação de amizade rejeitada'})
        else:
            return Response({'error': 'Solicitação de amizade não encontrada'}, 
                           status=status.HTTP_404_NOT_FOUND)
            
    except User.DoesNotExist:
        return Response({'error': 'Usuário não encontrado'}, 
                       status=status.HTTP_404_NOT_FOUND)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Perfil não encontrado'}, 
                       status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friends(request):
    """Listar amigos do usuário"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if hasattr(user_profile, 'friends') and user_profile.friends:
            friends = User.objects.filter(id__in=user_profile.friends)
            serializer = UserProfileSerializer(friends, many=True, context={'request': request})
            return Response(serializer.data)
        else:
            return Response([])
            
    except UserProfile.DoesNotExist:
        return Response([])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_followers(request):
    """Listar seguidores do usuário"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if hasattr(user_profile, 'followers') and user_profile.followers:
            followers = User.objects.filter(id__in=user_profile.followers)
            serializer = UserProfileSerializer(followers, many=True, context={'request': request})
            return Response(serializer.data)
        else:
            return Response([])
            
    except UserProfile.DoesNotExist:
        return Response([])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_following(request):
    """Listar usuários que o usuário está seguindo"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if hasattr(user_profile, 'following') and user_profile.following:
            following = User.objects.filter(id__in=user_profile.following)
            serializer = UserProfileSerializer(following, many=True, context={'request': request})
            return Response(serializer.data)
        else:
            return Response([])
            
    except UserProfile.DoesNotExist:
        return Response([])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def social_feed(request):
    """Feed de atividades sociais"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Obter IDs dos amigos e usuários seguidos
        friend_ids = getattr(user_profile, 'friends', [])
        following_ids = getattr(user_profile, 'following', [])
        
        # Combinar todas as pessoas que o usuário segue
        social_network_ids = list(set(friend_ids + following_ids + [request.user.id]))
        
        # Buscar atividades recentes da rede social
        activities = UserActivity.objects.filter(
            user_id__in=social_network_ids
        ).select_related('user').order_by('-created_at')[:50]
        
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)
        
    except UserProfile.DoesNotExist:
        # Se não tem perfil, retornar apenas suas próprias atividades
        activities = UserActivity.objects.filter(
            user=request.user
        ).select_related('user').order_by('-created_at')[:20]
        
        serializer = UserActivitySerializer(activities, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def social_stats(request):
    """Estatísticas sociais do usuário"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        stats = {
            'friends_count': len(getattr(user_profile, 'friends', [])),
            'followers_count': len(getattr(user_profile, 'followers', [])),
            'following_count': len(getattr(user_profile, 'following', [])),
            'friend_requests_received': len(getattr(user_profile, 'friend_requests_received', [])),
            'friend_requests_sent': len(getattr(user_profile, 'friend_requests_sent', [])),
        }
        
        return Response(stats)
        
    except UserProfile.DoesNotExist:
        return Response({
            'friends_count': 0,
            'followers_count': 0,
            'following_count': 0,
            'friend_requests_received': 0,
            'friend_requests_sent': 0,
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def friend_requests(request):
    """Listar solicitações de amizade recebidas"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if hasattr(user_profile, 'friend_requests_received') and user_profile.friend_requests_received:
            requesters = User.objects.filter(id__in=user_profile.friend_requests_received)
            serializer = UserProfileSerializer(requesters, many=True, context={'request': request})
            return Response(serializer.data)
        else:
            return Response([])
            
    except UserProfile.DoesNotExist:
        return Response([])

def get_friend_user_ids(user):
    """Função auxiliar para pegar IDs dos amigos"""
    friend_ids = Friendship.objects.filter(
        Q(user1=user) | Q(user2=user),
        status='accepted'
    ).values_list('user1_id', 'user2_id')
    
    friend_user_ids = set()
    for user1_id, user2_id in friend_ids:
        friend_user_ids.update([user1_id, user2_id])
    friend_user_ids.discard(user.id)
    
    return list(friend_user_ids)

def is_user_online(last_activity):
    """Verifica se usuário está online (ativo nos últimos 5 minutos)"""
    return timezone.now() - last_activity < timedelta(minutes=5)

def get_time_ago(created_at):
    """Calcula tempo relativo"""
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