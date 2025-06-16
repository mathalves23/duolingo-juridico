"""
Views para o sistema de gamificação do Duolingo Jurídico
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Max, Min
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta, date

from .models import (
    Achievement, UserAchievement, Leaderboard, LeaderboardEntry,
    StoreItem, UserPurchase, UserBoost, DailyChallenge, DailyChallengeCompletion
)
from .serializers import (
    AchievementSerializer, AchievementListSerializer,
    UserAchievementSerializer, LeaderboardSerializer, LeaderboardListSerializer,
    StoreItemSerializer, StoreItemListSerializer, UserPurchaseSerializer,
    UserBoostSerializer, DailyChallengeSerializer, DailyChallengeCompletionSerializer,
    GamificationStatsSerializer
)

User = get_user_model()


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para conquistas"""
    
    queryset = Achievement.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AchievementListSerializer
        return AchievementSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar conquistas secretas se não autenticado
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_secret=False)
        
        # Filtrar por tipo
        achievement_type = self.request.query_params.get('type')
        if achievement_type:
            queryset = queryset.filter(achievement_type=achievement_type)
        
        # Filtrar por raridade
        rarity = self.request.query_params.get('rarity')
        if rarity:
            queryset = queryset.filter(rarity=rarity)
        
        # Filtrar por status do usuário
        if self.request.user.is_authenticated:
            user_status = self.request.query_params.get('status')
            if user_status == 'unlocked':
                queryset = queryset.filter(
                    unlocked_by__user=self.request.user
                )
            elif user_status == 'locked':
                queryset = queryset.exclude(
                    unlocked_by__user=self.request.user
                )
        
        return queryset.order_by('achievement_type', 'name')
    
    @action(detail=False, methods=['get'])
    def check_unlocks(self, request):
        """Verificar conquistas desbloqueáveis para o usuário"""
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticação necessária'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        user = request.user
        unlocked_achievements = []
        
        # Verificar todas as conquistas ativas
        for achievement in Achievement.objects.filter(is_active=True):
            # Pular se já foi desbloqueada
            if UserAchievement.objects.filter(
                user=user, 
                achievement=achievement
            ).exists():
                continue
            
            # Verificar se atende aos requisitos
            if achievement.check_requirements(user):
                # Desbloquear conquista
                user_achievement = UserAchievement.objects.create(
                    user=user,
                    achievement=achievement,
                    xp_received=achievement.xp_reward,
                    coins_received=achievement.coin_reward,
                    gems_received=achievement.gem_reward
                )
                
                # Atualizar contadores do usuário
                user.total_xp += achievement.xp_reward
                user.total_coins += achievement.coin_reward
                user.total_gems += achievement.gem_reward
                user.save()
                
                # Atualizar contador da conquista
                achievement.unlock_count += 1
                achievement.save()
                
                unlocked_achievements.append(
                    UserAchievementSerializer(user_achievement).data
                )
        
        return Response({
            'newly_unlocked': unlocked_achievements,
            'total_unlocked': len(unlocked_achievements)
        })


class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para conquistas do usuário"""
    
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas das conquistas do usuário"""
        user_achievements = self.get_queryset()
        
        # Estatísticas por raridade
        rarity_stats = {}
        for rarity, rarity_name in Achievement.RARITY_LEVELS:
            count = user_achievements.filter(
                achievement__rarity=rarity
            ).count()
            rarity_stats[rarity] = {
                'name': rarity_name,
                'unlocked': count,
                'total': Achievement.objects.filter(
                    is_active=True, 
                    rarity=rarity
                ).count()
            }
        
        # Recompensas totais recebidas
        total_xp = sum(ua.xp_received for ua in user_achievements)
        total_coins = sum(ua.coins_received for ua in user_achievements)
        total_gems = sum(ua.gems_received for ua in user_achievements)
        
        return Response({
            'total_achievements': user_achievements.count(),
            'total_possible': Achievement.objects.filter(is_active=True).count(),
            'completion_rate': round(
                (user_achievements.count() / Achievement.objects.filter(is_active=True).count()) * 100, 2
            ) if Achievement.objects.filter(is_active=True).exists() else 0,
            'rarity_breakdown': rarity_stats,
            'total_rewards': {
                'xp': total_xp,
                'coins': total_coins,
                'gems': total_gems
            }
        })


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para rankings"""
    
    queryset = Leaderboard.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LeaderboardListSerializer
        return LeaderboardSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por tipo
        leaderboard_type = self.request.query_params.get('type')
        if leaderboard_type:
            queryset = queryset.filter(leaderboard_type=leaderboard_type)
        
        # Filtrar por período
        period = self.request.query_params.get('period')
        if period:
            queryset = queryset.filter(period=period)
        
        return queryset.order_by('leaderboard_type', 'period')
    
    @action(detail=True, methods=['post'])
    def update_rankings(self, request, pk=None):
        """Atualizar rankings (apenas admin)"""
        if not request.user.is_staff:
            return Response({'error': 'Permissão negada'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        leaderboard = self.get_object()
        leaderboard.update_rankings()
        
        return Response({'message': 'Rankings atualizados com sucesso'})


class StoreItemViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para itens da loja"""
    
    queryset = StoreItem.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return StoreItemListSerializer
        return StoreItemSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por tipo
        item_type = self.request.query_params.get('type')
        if item_type:
            queryset = queryset.filter(item_type=item_type)
        
        # Filtrar apenas itens disponíveis
        available_only = self.request.query_params.get('available_only', 'false')
        if available_only.lower() == 'true':
            now = timezone.now()
            queryset = queryset.filter(
                Q(available_from__isnull=True) | Q(available_from__lte=now),
                Q(available_until__isnull=True) | Q(available_until__gte=now)
            )
        
        return queryset.order_by('item_type', 'name')
    
    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        """Comprar um item"""
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticação necessária'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        item = self.get_object()
        user = request.user
        payment_method = request.data.get('payment_method', 'coins')
        quantity = int(request.data.get('quantity', 1))
        
        # Verificar se o item está disponível
        if not item.is_available:
            return Response({'error': 'Item não disponível'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar se já possui (para itens únicos)
        if item.item_type in ['avatar', 'theme'] and UserPurchase.objects.filter(
            user=user, item=item, status='completed'
        ).exists():
            return Response({'error': 'Você já possui este item'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Calcular custos
        coins_cost = (item.coin_price or 0) * quantity
        gems_cost = (item.gem_price or 0) * quantity
        real_cost = (item.real_price or 0) * quantity
        
        # Verificar se tem recursos suficientes
        if payment_method == 'coins':
            if user.total_coins < coins_cost:
                return Response({'error': 'Moedas insuficientes'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        elif payment_method == 'gems':
            if user.total_gems < gems_cost:
                return Response({'error': 'Gemas insuficientes'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        
        # Criar compra
        purchase = UserPurchase.objects.create(
            user=user,
            item=item,
            quantity=quantity,
            payment_method=payment_method,
            coins_spent=coins_cost if payment_method == 'coins' else 0,
            gems_spent=gems_cost if payment_method == 'gems' else 0,
            real_amount=real_cost if payment_method not in ['coins', 'gems'] else 0
        )
        
        # Processar pagamento
        if payment_method in ['coins', 'gems']:
            purchase.complete_purchase()
        
        serializer = UserPurchaseSerializer(purchase)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserPurchaseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para compras do usuário"""
    
    serializer_class = UserPurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserPurchase.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas de compras do usuário"""
        purchases = self.get_queryset().filter(status='completed')
        
        return Response({
            'total_purchases': purchases.count(),
            'total_coins_spent': sum(p.coins_spent for p in purchases),
            'total_gems_spent': sum(p.gems_spent for p in purchases),
            'total_real_spent': sum(p.real_amount for p in purchases),
            'favorite_category': purchases.values('item__item_type').annotate(
                count=Count('id')
            ).order_by('-count').first()
        })


class UserBoostViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para impulsos ativos do usuário"""
    
    serializer_class = UserBoostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserBoost.objects.filter(
            user=self.request.user,
            is_active=True
        )
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Impulsos ativos do usuário"""
        boosts = self.get_queryset().filter(expires_at__gt=timezone.now())
        serializer = self.get_serializer(boosts, many=True)
        
        return Response({
            'active_boosts': serializer.data,
            'total_active': boosts.count()
        })


class DailyChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para desafios diários"""
    
    serializer_class = DailyChallengeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = DailyChallenge.objects.filter(is_active=True)
        
        # Filtrar por data
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(date=date_param)
        else:
            # Por padrão, apenas o desafio de hoje
            queryset = queryset.filter(date=date.today())
        
        return queryset.order_by('-date')
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Desafio de hoje"""
        today_challenge = DailyChallenge.objects.filter(
            date=date.today(),
            is_active=True
        ).first()
        
        if not today_challenge:
            return Response({'message': 'Nenhum desafio disponível hoje'})
        
        serializer = self.get_serializer(today_challenge)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Completar um desafio diário"""
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticação necessária'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        challenge = self.get_object()
        
        # Verificar se já foi completado
        user_challenge, created = DailyChallengeCompletion.objects.get_or_create(
            user=request.user,
            challenge=challenge,
            defaults={'target': challenge.requirements.get('target', 1)}
        )
        
        if user_challenge.completed:
            return Response({'error': 'Desafio já completado'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Atualizar progresso (forçar conclusão se admin)
        if request.user.is_staff:
            user_challenge.progress = user_challenge.target
        else:
            progress_amount = request.data.get('progress', 1)
            user_challenge.update_progress(progress_amount)
        
        serializer = DailyChallengeCompletionSerializer(user_challenge)
        return Response(serializer.data)


class DailyChallengeCompletionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para progresso em desafios diários"""
    
    serializer_class = DailyChallengeCompletionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DailyChallengeCompletion.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas dos desafios do usuário"""
        user_completions = self.get_queryset()
        today = timezone.now().date()
        
        # Streak atual
        current_streak = 0
        check_date = today
        while True:
            if user_completions.filter(
                daily_challenge__date=check_date,
                completed=True
            ).exists():
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break
        
        # Estatísticas gerais
        total_completed = user_completions.filter(completed=True).count()
        total_available = DailyChallenge.objects.filter(
            date__lte=today
        ).count()
        
        return Response({
            'current_streak': current_streak,
            'total_completed': total_completed,
            'total_available': total_available,
            'completion_rate': round(
                (total_completed / total_available) * 100, 2
            ) if total_available > 0 else 0,
            'this_week_completed': user_completions.filter(
                daily_challenge__date__gte=today - timedelta(days=7),
                completed=True
            ).count()
        })


# Views para endpoints customizados
class GamificationStatsView(viewsets.ViewSet):
    """ViewSet para estatísticas gerais de gamificação"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard completo de gamificação"""
        user = request.user
        
        # Calcular nível baseado no XP
        # Fórmula: level = sqrt(total_xp / 100)
        import math
        current_level = int(math.sqrt(user.total_xp / 100)) + 1
        xp_for_current_level = (current_level - 1) ** 2 * 100
        xp_for_next_level = current_level ** 2 * 100
        level_progress = user.total_xp - xp_for_current_level
        level_total = xp_for_next_level - xp_for_current_level
        level_progress_percentage = (level_progress / level_total) * 100 if level_total > 0 else 0
        
        # Conquistas por raridade
        achievements_by_rarity = {}
        for rarity, rarity_name in Achievement.RARITY_LEVELS:
            user_count = UserAchievement.objects.filter(
                user=user,
                achievement__rarity=rarity
            ).count()
            total_count = Achievement.objects.filter(
                is_active=True,
                rarity=rarity
            ).count()
            achievements_by_rarity[rarity] = {
                'name': rarity_name,
                'unlocked': user_count,
                'total': total_count
            }
        
        # Melhor posição nos rankings
        best_position = LeaderboardEntry.objects.filter(
            user=user
        ).aggregate(best=Min('position'))['best'] or 999
        
        # Rankings atuais
        current_rankings = []
        for entry in LeaderboardEntry.objects.filter(user=user)[:5]:
            current_rankings.append({
                'leaderboard': entry.leaderboard.name,
                'position': entry.position,
                'score': entry.score
            })
        
        # Estatísticas de atividade
        lessons_completed = user.user_lessons.filter(completed=True).count()
        quizzes_completed = user.quiz_attempts.filter(status='completed').count()
        
        # Taxa de acerto
        user_answers = user.user_answers.all()
        accuracy_rate = 0
        if user_answers.exists():
            correct_answers = user_answers.filter(is_correct=True).count()
            accuracy_rate = (correct_answers / user_answers.count()) * 100
        
        stats_data = {
            'total_xp': user.total_xp,
            'current_level': current_level,
            'xp_for_next_level': xp_for_next_level - user.total_xp,
            'level_progress_percentage': round(level_progress_percentage, 2),
            'total_coins': user.total_coins,
            'total_gems': user.total_gems,
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
            'total_achievements': UserAchievement.objects.filter(user=user).count(),
            'achievements_by_rarity': achievements_by_rarity,
            'best_ranking_position': best_position,
            'current_rankings': current_rankings,
            'lessons_completed': lessons_completed,
            'quizzes_completed': quizzes_completed,
            'accuracy_rate': round(accuracy_rate, 2)
        }
        
        serializer = GamificationStatsSerializer(data=stats_data)
        serializer.is_valid()
        return Response(serializer.data)
