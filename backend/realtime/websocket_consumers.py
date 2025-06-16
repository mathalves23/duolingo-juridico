"""
Sistema WebSocket Avançado - Duolingo Jurídico
Comunicação em tempo real, colaboração e notificações instantâneas
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

User = get_user_model()

class MessageType(Enum):
    # Sistema
    SYSTEM_NOTIFICATION = "system_notification"
    USER_STATUS = "user_status"
    HEARTBEAT = "heartbeat"
    
    # Aprendizado
    LESSON_PROGRESS = "lesson_progress"
    QUIZ_RESULT = "quiz_result"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"
    STREAK_UPDATE = "streak_update"
    
    # Social
    FRIEND_ACTIVITY = "friend_activity"
    LEADERBOARD_UPDATE = "leaderboard_update"
    CHAT_MESSAGE = "chat_message"
    STUDY_GROUP_UPDATE = "study_group_update"
    
    # Colaboração
    COLLABORATIVE_EDIT = "collaborative_edit"
    DOCUMENT_LOCK = "document_lock"
    CURSOR_POSITION = "cursor_position"
    
    # Gamificação
    CHALLENGE_INVITE = "challenge_invite"
    TOURNAMENT_UPDATE = "tournament_update"
    LIVE_COMPETITION = "live_competition"
    
    # Admin/Monitoring
    ADMIN_ALERT = "admin_alert"
    SYSTEM_METRICS = "system_metrics"
    USER_ANALYTICS = "user_analytics"

@dataclass
class WebSocketMessage:
    """Mensagem WebSocket estruturada"""
    type: MessageType
    data: Dict[str, Any]
    timestamp: datetime
    sender_id: Optional[str] = None
    target_users: Optional[List[str]] = None
    room: Optional[str] = None
    priority: str = "normal"  # low, normal, high, critical

class ConnectionManager:
    """Gerenciador de conexões WebSocket"""
    
    def __init__(self):
        self.connections: Dict[str, Set[str]] = {}  # user_id -> set of channel_names
        self.rooms: Dict[str, Set[str]] = {}  # room_name -> set of channel_names
        self.user_channels: Dict[str, str] = {}  # channel_name -> user_id
        self.channel_metadata: Dict[str, Dict] = {}  # channel_name -> metadata
        self.logger = logging.getLogger(__name__)
    
    def add_connection(self, channel_name: str, user_id: str, metadata: Dict = None):
        """Adiciona nova conexão"""
        if user_id not in self.connections:
            self.connections[user_id] = set()
        
        self.connections[user_id].add(channel_name)
        self.user_channels[channel_name] = user_id
        self.channel_metadata[channel_name] = metadata or {}
        
        self.logger.info(f"User {user_id} connected via {channel_name}")
    
    def remove_connection(self, channel_name: str):
        """Remove conexão"""
        if channel_name in self.user_channels:
            user_id = self.user_channels[channel_name]
            
            if user_id in self.connections:
                self.connections[user_id].discard(channel_name)
                if not self.connections[user_id]:
                    del self.connections[user_id]
            
            del self.user_channels[channel_name]
            
            if channel_name in self.channel_metadata:
                del self.channel_metadata[channel_name]
            
            # Remove de todas as salas
            for room_channels in self.rooms.values():
                room_channels.discard(channel_name)
            
            self.logger.info(f"Connection {channel_name} removed")
    
    def join_room(self, channel_name: str, room_name: str):
        """Adiciona canal a uma sala"""
        if room_name not in self.rooms:
            self.rooms[room_name] = set()
        
        self.rooms[room_name].add(channel_name)
        self.logger.info(f"Channel {channel_name} joined room {room_name}")
    
    def leave_room(self, channel_name: str, room_name: str):
        """Remove canal de uma sala"""
        if room_name in self.rooms:
            self.rooms[room_name].discard(channel_name)
            if not self.rooms[room_name]:
                del self.rooms[room_name]
    
    def get_user_channels(self, user_id: str) -> Set[str]:
        """Obtém canais de um usuário"""
        return self.connections.get(user_id, set())
    
    def get_room_channels(self, room_name: str) -> Set[str]:
        """Obtém canais de uma sala"""
        return self.rooms.get(room_name, set())
    
    def get_online_users(self) -> List[str]:
        """Obtém lista de usuários online"""
        return list(self.connections.keys())
    
    def is_user_online(self, user_id: str) -> bool:
        """Verifica se usuário está online"""
        return user_id in self.connections and len(self.connections[user_id]) > 0

# Instância global do gerenciador
connection_manager = ConnectionManager()

class BaseWebSocketConsumer(AsyncWebsocketConsumer):
    """Consumer base com funcionalidades comuns"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None
        self.rooms = set()
        self.last_heartbeat = None
        self.logger = logging.getLogger(__name__)
    
    async def connect(self):
        """Conecta WebSocket"""
        self.user_id = str(self.scope["user"].id) if self.scope["user"].is_authenticated else None
        
        if not self.user_id:
            await self.close()
            return
        
        await self.accept()
        
        # Adiciona conexão ao gerenciador
        connection_manager.add_connection(
            self.channel_name, 
            self.user_id,
            {
                'connected_at': timezone.now().isoformat(),
                'user_agent': self.scope.get('headers', {}).get('user-agent', ''),
                'ip_address': self.get_client_ip()
            }
        )
        
        # Envia confirmação de conexão
        await self.send_message(WebSocketMessage(
            type=MessageType.SYSTEM_NOTIFICATION,
            data={
                'message': 'Conectado com sucesso',
                'user_id': self.user_id,
                'timestamp': timezone.now().isoformat()
            },
            timestamp=timezone.now()
        ))
        
        # Inicia heartbeat
        asyncio.create_task(self.heartbeat_loop())
        
        self.logger.info(f"WebSocket connected for user {self.user_id}")
    
    async def disconnect(self, close_code):
        """Desconecta WebSocket"""
        # Remove de todas as salas
        for room in self.rooms:
            await self.channel_layer.group_discard(room, self.channel_name)
        
        # Remove conexão do gerenciador
        connection_manager.remove_connection(self.channel_name)
        
        self.logger.info(f"WebSocket disconnected for user {self.user_id}")
    
    async def receive(self, text_data):
        """Recebe mensagem do cliente"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            message_data = data.get('data', {})
            
            # Atualiza último heartbeat
            if message_type == 'heartbeat':
                self.last_heartbeat = timezone.now()
                await self.send_message(WebSocketMessage(
                    type=MessageType.HEARTBEAT,
                    data={'status': 'alive', 'timestamp': timezone.now().isoformat()},
                    timestamp=timezone.now()
                ))
                return
            
            # Processa mensagem
            await self.handle_message(message_type, message_data)
            
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            await self.send_error("Internal error processing message")
    
    async def handle_message(self, message_type: str, data: Dict[str, Any]):
        """Processa mensagem recebida (implementar em subclasses)"""
        pass
    
    async def send_message(self, message: WebSocketMessage):
        """Envia mensagem estruturada"""
        await self.send(text_data=json.dumps({
            'type': message.type.value,
            'data': message.data,
            'timestamp': message.timestamp.isoformat(),
            'sender_id': message.sender_id,
            'priority': message.priority
        }))
    
    async def send_error(self, error_message: str):
        """Envia mensagem de erro"""
        await self.send_message(WebSocketMessage(
            type=MessageType.SYSTEM_NOTIFICATION,
            data={
                'error': True,
                'message': error_message
            },
            timestamp=timezone.now()
        ))
    
    async def heartbeat_loop(self):
        """Loop de heartbeat para manter conexão viva"""
        while True:
            try:
                await asyncio.sleep(30)  # Heartbeat a cada 30 segundos
                
                # Verifica se conexão ainda está ativa
                if self.last_heartbeat and (timezone.now() - self.last_heartbeat).seconds > 120:
                    self.logger.warning(f"Heartbeat timeout for user {self.user_id}")
                    await self.close()
                    break
                
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                break
    
    def get_client_ip(self) -> str:
        """Obtém IP do cliente"""
        headers = dict(self.scope.get('headers', []))
        x_forwarded_for = headers.get(b'x-forwarded-for')
        
        if x_forwarded_for:
            return x_forwarded_for.decode().split(',')[0].strip()
        
        return self.scope.get('client', ['unknown'])[0]

class LearningWebSocketConsumer(BaseWebSocketConsumer):
    """Consumer para funcionalidades de aprendizado"""
    
    async def connect(self):
        await super().connect()
        
        # Entra na sala geral de aprendizado
        await self.join_room('learning_general')
        
        # Entra na sala específica do usuário
        await self.join_room(f'user_{self.user_id}')
    
    async def join_room(self, room_name: str):
        """Entra em uma sala"""
        await self.channel_layer.group_add(room_name, self.channel_name)
        connection_manager.join_room(self.channel_name, room_name)
        self.rooms.add(room_name)
    
    async def leave_room(self, room_name: str):
        """Sai de uma sala"""
        await self.channel_layer.group_discard(room_name, self.channel_name)
        connection_manager.leave_room(self.channel_name, room_name)
        self.rooms.discard(room_name)
    
    async def handle_message(self, message_type: str, data: Dict[str, Any]):
        """Processa mensagens de aprendizado"""
        
        if message_type == 'join_lesson':
            lesson_id = data.get('lesson_id')
            if lesson_id:
                await self.join_room(f'lesson_{lesson_id}')
                await self.send_message(WebSocketMessage(
                    type=MessageType.LESSON_PROGRESS,
                    data={'joined_lesson': lesson_id},
                    timestamp=timezone.now()
                ))
        
        elif message_type == 'lesson_progress':
            await self.broadcast_lesson_progress(data)
        
        elif message_type == 'quiz_answer':
            await self.handle_quiz_answer(data)
        
        elif message_type == 'request_help':
            await self.handle_help_request(data)
    
    async def broadcast_lesson_progress(self, data: Dict[str, Any]):
        """Transmite progresso da lição"""
        lesson_id = data.get('lesson_id')
        progress = data.get('progress', 0)
        
        if lesson_id:
            # Envia para outros usuários na mesma lição
            await self.channel_layer.group_send(
                f'lesson_{lesson_id}',
                {
                    'type': 'lesson_progress_update',
                    'user_id': self.user_id,
                    'lesson_id': lesson_id,
                    'progress': progress,
                    'timestamp': timezone.now().isoformat()
                }
            )
    
    async def handle_quiz_answer(self, data: Dict[str, Any]):
        """Processa resposta de quiz"""
        quiz_id = data.get('quiz_id')
        answer = data.get('answer')
        is_correct = data.get('is_correct', False)
        
        # Envia resultado para o usuário
        await self.send_message(WebSocketMessage(
            type=MessageType.QUIZ_RESULT,
            data={
                'quiz_id': quiz_id,
                'answer': answer,
                'is_correct': is_correct,
                'timestamp': timezone.now().isoformat()
            },
            timestamp=timezone.now()
        ))
        
        # Se resposta correta, verifica conquistas
        if is_correct:
            await self.check_achievements(quiz_id)
    
    async def handle_help_request(self, data: Dict[str, Any]):
        """Processa pedido de ajuda"""
        lesson_id = data.get('lesson_id')
        question = data.get('question')
        
        # Notifica outros usuários na mesma lição
        await self.channel_layer.group_send(
            f'lesson_{lesson_id}',
            {
                'type': 'help_request',
                'user_id': self.user_id,
                'lesson_id': lesson_id,
                'question': question,
                'timestamp': timezone.now().isoformat()
            }
        )
    
    async def check_achievements(self, quiz_id: str):
        """Verifica se desbloqueou conquistas"""
        # Simula verificação de conquistas
        # Em produção, integrar com sistema de gamificação
        
        achievement = {
            'id': 'quiz_master',
            'title': 'Mestre dos Quizzes',
            'description': 'Acertou 10 quizzes consecutivos',
            'icon': '🏆',
            'xp_reward': 100
        }
        
        await self.send_message(WebSocketMessage(
            type=MessageType.ACHIEVEMENT_UNLOCK,
            data=achievement,
            timestamp=timezone.now()
        ))
    
    # Handlers para mensagens do grupo
    
    async def lesson_progress_update(self, event):
        """Recebe atualização de progresso da lição"""
        await self.send_message(WebSocketMessage(
            type=MessageType.LESSON_PROGRESS,
            data=event,
            timestamp=timezone.now()
        ))
    
    async def help_request(self, event):
        """Recebe pedido de ajuda"""
        if event['user_id'] != self.user_id:  # Não enviar para quem pediu ajuda
            await self.send_message(WebSocketMessage(
                type=MessageType.CHAT_MESSAGE,
                data={
                    'type': 'help_request',
                    'from_user': event['user_id'],
                    'lesson_id': event['lesson_id'],
                    'question': event['question'],
                    'timestamp': event['timestamp']
                },
                timestamp=timezone.now()
            ))

class SocialWebSocketConsumer(BaseWebSocketConsumer):
    """Consumer para funcionalidades sociais"""
    
    async def connect(self):
        await super().connect()
        
        # Entra na sala social geral
        await self.join_room('social_general')
        
        # Notifica amigos que usuário ficou online
        await self.notify_friends_status('online')
    
    async def disconnect(self, close_code):
        # Notifica amigos que usuário ficou offline
        await self.notify_friends_status('offline')
        await super().disconnect(close_code)
    
    async def join_room(self, room_name: str):
        """Entra em uma sala"""
        await self.channel_layer.group_add(room_name, self.channel_name)
        connection_manager.join_room(self.channel_name, room_name)
        self.rooms.add(room_name)
    
    async def handle_message(self, message_type: str, data: Dict[str, Any]):
        """Processa mensagens sociais"""
        
        if message_type == 'send_chat_message':
            await self.handle_chat_message(data)
        
        elif message_type == 'join_study_group':
            await self.join_study_group(data.get('group_id'))
        
        elif message_type == 'challenge_friend':
            await self.challenge_friend(data)
        
        elif message_type == 'update_status':
            await self.update_user_status(data)
    
    async def handle_chat_message(self, data: Dict[str, Any]):
        """Processa mensagem de chat"""
        room = data.get('room', 'social_general')
        message = data.get('message')
        
        if message and room in self.rooms:
            # Envia mensagem para todos na sala
            await self.channel_layer.group_send(
                room,
                {
                    'type': 'chat_message_broadcast',
                    'user_id': self.user_id,
                    'message': message,
                    'room': room,
                    'timestamp': timezone.now().isoformat()
                }
            )
    
    async def join_study_group(self, group_id: str):
        """Entra em grupo de estudos"""
        if group_id:
            room_name = f'study_group_{group_id}'
            await self.join_room(room_name)
            
            # Notifica outros membros
            await self.channel_layer.group_send(
                room_name,
                {
                    'type': 'study_group_member_joined',
                    'user_id': self.user_id,
                    'group_id': group_id,
                    'timestamp': timezone.now().isoformat()
                }
            )
    
    async def challenge_friend(self, data: Dict[str, Any]):
        """Desafia amigo"""
        friend_id = data.get('friend_id')
        challenge_type = data.get('challenge_type')
        
        if friend_id:
            # Envia desafio para o amigo
            friend_channels = connection_manager.get_user_channels(friend_id)
            
            for channel in friend_channels:
                await self.channel_layer.send(
                    channel,
                    {
                        'type': 'challenge_received',
                        'from_user': self.user_id,
                        'challenge_type': challenge_type,
                        'timestamp': timezone.now().isoformat()
                    }
                )
    
    async def update_user_status(self, data: Dict[str, Any]):
        """Atualiza status do usuário"""
        status = data.get('status')
        activity = data.get('activity')
        
        # Notifica amigos sobre mudança de status
        await self.notify_friends_status(status, activity)
    
    async def notify_friends_status(self, status: str, activity: str = None):
        """Notifica amigos sobre status"""
        # Em produção, buscar lista de amigos do banco
        friends = await self.get_user_friends()
        
        for friend_id in friends:
            friend_channels = connection_manager.get_user_channels(friend_id)
            
            for channel in friend_channels:
                await self.channel_layer.send(
                    channel,
                    {
                        'type': 'friend_status_update',
                        'user_id': self.user_id,
                        'status': status,
                        'activity': activity,
                        'timestamp': timezone.now().isoformat()
                    }
                )
    
    @database_sync_to_async
    def get_user_friends(self) -> List[str]:
        """Obtém lista de amigos do usuário"""
        # Simula lista de amigos
        return ['friend1', 'friend2', 'friend3']
    
    # Handlers para mensagens do grupo
    
    async def chat_message_broadcast(self, event):
        """Transmite mensagem de chat"""
        if event['user_id'] != self.user_id:  # Não enviar para quem enviou
            await self.send_message(WebSocketMessage(
                type=MessageType.CHAT_MESSAGE,
                data=event,
                timestamp=timezone.now()
            ))
    
    async def study_group_member_joined(self, event):
        """Notifica que membro entrou no grupo"""
        if event['user_id'] != self.user_id:
            await self.send_message(WebSocketMessage(
                type=MessageType.STUDY_GROUP_UPDATE,
                data={
                    'action': 'member_joined',
                    'user_id': event['user_id'],
                    'group_id': event['group_id']
                },
                timestamp=timezone.now()
            ))
    
    async def friend_status_update(self, event):
        """Recebe atualização de status de amigo"""
        await self.send_message(WebSocketMessage(
            type=MessageType.FRIEND_ACTIVITY,
            data=event,
            timestamp=timezone.now()
        ))
    
    async def challenge_received(self, event):
        """Recebe desafio de amigo"""
        await self.send_message(WebSocketMessage(
            type=MessageType.CHALLENGE_INVITE,
            data=event,
            timestamp=timezone.now()
        ))

class AdminWebSocketConsumer(BaseWebSocketConsumer):
    """Consumer para funcionalidades administrativas"""
    
    async def connect(self):
        # Verifica se usuário é admin
        if not self.scope["user"].is_staff:
            await self.close()
            return
        
        await super().connect()
        
        # Entra na sala de administradores
        await self.join_room('admin_dashboard')
        
        # Inicia envio de métricas em tempo real
        asyncio.create_task(self.metrics_loop())
    
    async def join_room(self, room_name: str):
        """Entra em uma sala"""
        await self.channel_layer.group_add(room_name, self.channel_name)
        connection_manager.join_room(self.channel_name, room_name)
        self.rooms.add(room_name)
    
    async def handle_message(self, message_type: str, data: Dict[str, Any]):
        """Processa mensagens administrativas"""
        
        if message_type == 'request_metrics':
            await self.send_current_metrics()
        
        elif message_type == 'send_announcement':
            await self.send_system_announcement(data)
        
        elif message_type == 'moderate_content':
            await self.moderate_content(data)
    
    async def send_current_metrics(self):
        """Envia métricas atuais"""
        metrics = {
            'online_users': len(connection_manager.get_online_users()),
            'active_connections': sum(len(channels) for channels in connection_manager.connections.values()),
            'active_rooms': len(connection_manager.rooms),
            'system_load': 45.2,  # Simulado
            'memory_usage': 62.8,  # Simulado
            'timestamp': timezone.now().isoformat()
        }
        
        await self.send_message(WebSocketMessage(
            type=MessageType.SYSTEM_METRICS,
            data=metrics,
            timestamp=timezone.now()
        ))
    
    async def send_system_announcement(self, data: Dict[str, Any]):
        """Envia anúncio do sistema"""
        message = data.get('message')
        priority = data.get('priority', 'normal')
        target_users = data.get('target_users', [])
        
        announcement = {
            'message': message,
            'priority': priority,
            'from_admin': self.user_id,
            'timestamp': timezone.now().isoformat()
        }
        
        if target_users:
            # Envia para usuários específicos
            for user_id in target_users:
                user_channels = connection_manager.get_user_channels(user_id)
                for channel in user_channels:
                    await self.channel_layer.send(
                        channel,
                        {
                            'type': 'system_announcement',
                            'data': announcement
                        }
                    )
        else:
            # Envia para todos os usuários online
            for user_id in connection_manager.get_online_users():
                user_channels = connection_manager.get_user_channels(user_id)
                for channel in user_channels:
                    await self.channel_layer.send(
                        channel,
                        {
                            'type': 'system_announcement',
                            'data': announcement
                        }
                    )
    
    async def moderate_content(self, data: Dict[str, Any]):
        """Modera conteúdo"""
        content_id = data.get('content_id')
        action = data.get('action')  # 'approve', 'reject', 'flag'
        reason = data.get('reason', '')
        
        # Processa moderação
        moderation_result = {
            'content_id': content_id,
            'action': action,
            'reason': reason,
            'moderator': self.user_id,
            'timestamp': timezone.now().isoformat()
        }
        
        # Notifica outros admins
        await self.channel_layer.group_send(
            'admin_dashboard',
            {
                'type': 'moderation_action',
                'data': moderation_result
            }
        )
    
    async def metrics_loop(self):
        """Loop de envio de métricas"""
        while True:
            try:
                await asyncio.sleep(10)  # Atualiza a cada 10 segundos
                await self.send_current_metrics()
                
            except Exception as e:
                self.logger.error(f"Metrics loop error: {e}")
                break
    
    # Handlers para mensagens do grupo
    
    async def system_announcement(self, event):
        """Recebe anúncio do sistema"""
        await self.send_message(WebSocketMessage(
            type=MessageType.SYSTEM_NOTIFICATION,
            data=event['data'],
            timestamp=timezone.now()
        ))
    
    async def moderation_action(self, event):
        """Recebe ação de moderação"""
        if event['data']['moderator'] != self.user_id:  # Não enviar para quem fez a ação
            await self.send_message(WebSocketMessage(
                type=MessageType.ADMIN_ALERT,
                data=event['data'],
                timestamp=timezone.now()
            ))

# Funções utilitárias

async def broadcast_to_all_users(message: WebSocketMessage):
    """Transmite mensagem para todos os usuários online"""
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    
    for user_id in connection_manager.get_online_users():
        user_channels = connection_manager.get_user_channels(user_id)
        
        for channel in user_channels:
            await channel_layer.send(
                channel,
                {
                    'type': 'broadcast_message',
                    'message': asdict(message)
                }
            )

async def send_to_user(user_id: str, message: WebSocketMessage):
    """Envia mensagem para usuário específico"""
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    user_channels = connection_manager.get_user_channels(user_id)
    
    for channel in user_channels:
        await channel_layer.send(
            channel,
            {
                'type': 'direct_message',
                'message': asdict(message)
            }
        )

async def broadcast_to_room(room_name: str, message: WebSocketMessage):
    """Transmite mensagem para sala específica"""
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    
    await channel_layer.group_send(
        room_name,
        {
            'type': 'room_broadcast',
            'message': asdict(message)
        }
    )

def get_online_users_count() -> int:
    """Obtém número de usuários online"""
    return len(connection_manager.get_online_users())

def get_room_users_count(room_name: str) -> int:
    """Obtém número de usuários em uma sala"""
    return len(connection_manager.get_room_channels(room_name))

def is_user_online(user_id: str) -> bool:
    """Verifica se usuário está online"""
    return connection_manager.is_user_online(user_id) 