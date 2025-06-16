"""
Sistema de Monitoramento em Tempo Real - Duolingo Jurídico
Monitora performance, usuários, sistema e eventos críticos
"""

import asyncio
import json
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

import redis
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User = get_user_model()

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    active_connections: int
    database_connections: int
    cache_hit_rate: float
    response_time_avg: float
    error_rate: float

@dataclass
class UserActivityMetrics:
    """Métricas de atividade do usuário"""
    timestamp: datetime
    active_users: int
    new_registrations: int
    sessions_started: int
    questions_answered: int
    lessons_completed: int
    achievements_unlocked: int
    revenue_generated: float

@dataclass
class Alert:
    """Alerta do sistema"""
    id: str
    level: AlertLevel
    title: str
    message: str
    component: str
    timestamp: datetime
    is_resolved: bool = False
    resolution_time: Optional[datetime] = None

class RealTimeMonitor:
    """Monitor principal do sistema"""
    
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        self.channel_layer = get_channel_layer()
        self.is_running = False
        self.alerts: List[Alert] = []
        self.metrics_history: List[SystemMetrics] = []
        self.user_activity_history: List[UserActivityMetrics] = []
        
        # Configurações de limites
        self.thresholds = {
            'cpu_critical': 90.0,
            'cpu_warning': 75.0,
            'memory_critical': 90.0,
            'memory_warning': 80.0,
            'disk_critical': 95.0,
            'disk_warning': 85.0,
            'response_time_warning': 2000.0,  # ms
            'response_time_critical': 5000.0,  # ms
            'error_rate_warning': 5.0,  # %
            'error_rate_critical': 10.0,  # %
        }
        
        self.logger = logging.getLogger(__name__)
    
    async def start_monitoring(self):
        """Inicia o monitoramento contínuo"""
        self.is_running = True
        self.logger.info("Real-time monitoring started")
        
        # Tasks assíncronas para diferentes tipos de monitoramento
        tasks = [
            self.monitor_system_metrics(),
            self.monitor_user_activity(),
            self.monitor_database_performance(),
            self.monitor_api_endpoints(),
            self.process_alerts(),
            self.cleanup_old_data(),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop_monitoring(self):
        """Para o monitoramento"""
        self.is_running = False
        self.logger.info("Real-time monitoring stopped")
    
    async def monitor_system_metrics(self):
        """Monitora métricas do sistema"""
        while self.is_running:
            try:
                # Coleta métricas do sistema
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Conexões de rede
                net_connections = len(psutil.net_connections())
                
                # Conexões do banco
                db_connections = self.get_database_connections()
                
                # Cache hit rate
                cache_stats = self.get_cache_stats()
                
                # Response time médio
                avg_response_time = self.get_average_response_time()
                
                # Taxa de erro
                error_rate = self.get_error_rate()
                
                metrics = SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    disk_usage=disk.percent,
                    active_connections=net_connections,
                    database_connections=db_connections,
                    cache_hit_rate=cache_stats.get('hit_rate', 0.0),
                    response_time_avg=avg_response_time,
                    error_rate=error_rate
                )
                
                # Armazena métricas
                self.metrics_history.append(metrics)
                self.store_metrics_in_redis('system_metrics', metrics)
                
                # Verifica alertas
                await self.check_system_alerts(metrics)
                
                # Envia para WebSocket
                await self.broadcast_metrics('system_metrics', asdict(metrics))
                
                # Limita histórico (últimas 1000 entradas)
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                
            except Exception as e:
                self.logger.error(f"Error monitoring system metrics: {e}")
            
            await asyncio.sleep(30)  # Atualiza a cada 30 segundos
    
    async def monitor_user_activity(self):
        """Monitora atividade dos usuários"""
        while self.is_running:
            try:
                now = datetime.now()
                
                # Usuários ativos (últimos 5 minutos)
                active_users = self.get_active_users_count(minutes=5)
                
                # Novos registros (última hora)
                new_registrations = self.get_new_registrations_count(hours=1)
                
                # Sessões iniciadas (última hora)
                sessions_started = self.get_sessions_started_count(hours=1)
                
                # Questões respondidas (última hora)
                questions_answered = self.get_questions_answered_count(hours=1)
                
                # Lições completadas (última hora)
                lessons_completed = self.get_lessons_completed_count(hours=1)
                
                # Conquistas desbloqueadas (última hora)
                achievements_unlocked = self.get_achievements_unlocked_count(hours=1)
                
                # Receita gerada (última hora)
                revenue_generated = self.get_revenue_generated(hours=1)
                
                activity_metrics = UserActivityMetrics(
                    timestamp=now,
                    active_users=active_users,
                    new_registrations=new_registrations,
                    sessions_started=sessions_started,
                    questions_answered=questions_answered,
                    lessons_completed=lessons_completed,
                    achievements_unlocked=achievements_unlocked,
                    revenue_generated=revenue_generated
                )
                
                # Armazena métricas
                self.user_activity_history.append(activity_metrics)
                self.store_metrics_in_redis('user_activity', activity_metrics)
                
                # Envia para WebSocket
                await self.broadcast_metrics('user_activity', asdict(activity_metrics))
                
                # Limita histórico
                if len(self.user_activity_history) > 1000:
                    self.user_activity_history = self.user_activity_history[-1000:]
                
            except Exception as e:
                self.logger.error(f"Error monitoring user activity: {e}")
            
            await asyncio.sleep(60)  # Atualiza a cada minuto
    
    async def monitor_database_performance(self):
        """Monitora performance do banco de dados"""
        while self.is_running:
            try:
                # Consultas lentas
                slow_queries = self.get_slow_queries()
                
                # Bloqueios
                locks = self.get_database_locks()
                
                # Tamanho do banco
                db_size = self.get_database_size()
                
                # Índices não utilizados
                unused_indexes = self.get_unused_indexes()
                
                db_metrics = {
                    'timestamp': datetime.now(),
                    'slow_queries': slow_queries,
                    'active_locks': len(locks),
                    'database_size_mb': db_size,
                    'unused_indexes': len(unused_indexes)
                }
                
                # Verifica alertas
                if len(slow_queries) > 10:
                    await self.create_alert(
                        AlertLevel.WARNING,
                        "Database Performance",
                        f"Found {len(slow_queries)} slow queries",
                        "database"
                    )
                
                if len(locks) > 20:
                    await self.create_alert(
                        AlertLevel.CRITICAL,
                        "Database Locks",
                        f"Found {len(locks)} active locks",
                        "database"
                    )
                
                await self.broadcast_metrics('database_performance', db_metrics)
                
            except Exception as e:
                self.logger.error(f"Error monitoring database: {e}")
            
            await asyncio.sleep(120)  # Atualiza a cada 2 minutos
    
    async def monitor_api_endpoints(self):
        """Monitora performance dos endpoints da API"""
        while self.is_running:
            try:
                # Top endpoints mais usados
                top_endpoints = self.get_top_endpoints()
                
                # Endpoints com maior latência
                slow_endpoints = self.get_slow_endpoints()
                
                # Taxa de erro por endpoint
                error_rates = self.get_endpoint_error_rates()
                
                api_metrics = {
                    'timestamp': datetime.now(),
                    'top_endpoints': top_endpoints,
                    'slow_endpoints': slow_endpoints,
                    'error_rates': error_rates
                }
                
                # Verifica alertas para endpoints críticos
                for endpoint, error_rate in error_rates.items():
                    if error_rate > 10.0:
                        await self.create_alert(
                            AlertLevel.CRITICAL,
                            "API Endpoint Error",
                            f"Endpoint {endpoint} has {error_rate}% error rate",
                            "api"
                        )
                
                await self.broadcast_metrics('api_performance', api_metrics)
                
            except Exception as e:
                self.logger.error(f"Error monitoring API endpoints: {e}")
            
            await asyncio.sleep(180)  # Atualiza a cada 3 minutos
    
    async def check_system_alerts(self, metrics: SystemMetrics):
        """Verifica alertas do sistema baseado nas métricas"""
        
        # CPU
        if metrics.cpu_percent >= self.thresholds['cpu_critical']:
            await self.create_alert(
                AlertLevel.CRITICAL,
                "High CPU Usage",
                f"CPU usage is {metrics.cpu_percent}%",
                "system"
            )
        elif metrics.cpu_percent >= self.thresholds['cpu_warning']:
            await self.create_alert(
                AlertLevel.WARNING,
                "Elevated CPU Usage",
                f"CPU usage is {metrics.cpu_percent}%",
                "system"
            )
        
        # Memory
        if metrics.memory_percent >= self.thresholds['memory_critical']:
            await self.create_alert(
                AlertLevel.CRITICAL,
                "High Memory Usage",
                f"Memory usage is {metrics.memory_percent}%",
                "system"
            )
        elif metrics.memory_percent >= self.thresholds['memory_warning']:
            await self.create_alert(
                AlertLevel.WARNING,
                "Elevated Memory Usage",
                f"Memory usage is {metrics.memory_percent}%",
                "system"
            )
        
        # Response Time
        if metrics.response_time_avg >= self.thresholds['response_time_critical']:
            await self.create_alert(
                AlertLevel.CRITICAL,
                "High Response Time",
                f"Average response time is {metrics.response_time_avg}ms",
                "performance"
            )
        elif metrics.response_time_avg >= self.thresholds['response_time_warning']:
            await self.create_alert(
                AlertLevel.WARNING,
                "Elevated Response Time",
                f"Average response time is {metrics.response_time_avg}ms",
                "performance"
            )
    
    async def create_alert(self, level: AlertLevel, title: str, message: str, component: str):
        """Cria um novo alerta"""
        alert = Alert(
            id=f"{component}_{int(time.time())}",
            level=level,
            title=title,
            message=message,
            component=component,
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        
        # Armazena no Redis
        self.redis_client.lpush(
            'system_alerts',
            json.dumps(asdict(alert), default=str)
        )
        
        # Mantém apenas os últimos 100 alertas
        self.redis_client.ltrim('system_alerts', 0, 99)
        
        # Envia para WebSocket
        await self.broadcast_alert(alert)
        
        # Log do alerta
        self.logger.warning(f"Alert created: {level.value} - {title}: {message}")
    
    async def process_alerts(self):
        """Processa e resolve alertas automaticamente quando possível"""
        while self.is_running:
            try:
                for alert in self.alerts:
                    if alert.is_resolved:
                        continue
                    
                    # Verifica se condições do alerta ainda existem
                    if await self.should_resolve_alert(alert):
                        alert.is_resolved = True
                        alert.resolution_time = datetime.now()
                        
                        await self.broadcast_alert_resolved(alert)
                        self.logger.info(f"Alert resolved: {alert.title}")
                
            except Exception as e:
                self.logger.error(f"Error processing alerts: {e}")
            
            await asyncio.sleep(60)
    
    async def should_resolve_alert(self, alert: Alert) -> bool:
        """Verifica se um alerta deve ser resolvido automaticamente"""
        if alert.component == "system":
            current_metrics = self.metrics_history[-1] if self.metrics_history else None
            if not current_metrics:
                return False
            
            if "CPU" in alert.title:
                return current_metrics.cpu_percent < self.thresholds['cpu_warning']
            elif "Memory" in alert.title:
                return current_metrics.memory_percent < self.thresholds['memory_warning']
            elif "Response Time" in alert.title:
                return current_metrics.response_time_avg < self.thresholds['response_time_warning']
        
        return False
    
    async def cleanup_old_data(self):
        """Remove dados antigos para economizar memória"""
        while self.is_running:
            try:
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                # Remove métricas antigas
                self.metrics_history = [
                    m for m in self.metrics_history 
                    if m.timestamp > cutoff_time
                ]
                
                self.user_activity_history = [
                    m for m in self.user_activity_history 
                    if m.timestamp > cutoff_time
                ]
                
                # Remove alertas antigos resolvidos
                self.alerts = [
                    a for a in self.alerts 
                    if not a.is_resolved or a.timestamp > cutoff_time
                ]
                
            except Exception as e:
                self.logger.error(f"Error cleaning up old data: {e}")
            
            await asyncio.sleep(3600)  # Executa a cada hora
    
    # Métodos auxiliares de coleta de dados
    
    def get_database_connections(self) -> int:
        """Obtém número de conexões ativas do banco"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM pg_stat_activity;")
                return cursor.fetchone()[0]
        except:
            return 0
    
    def get_cache_stats(self) -> Dict[str, float]:
        """Obtém estatísticas do cache"""
        try:
            # Implementação específica para Redis
            info = self.redis_client.info()
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0
            
            return {
                'hit_rate': hit_rate,
                'hits': hits,
                'misses': misses
            }
        except:
            return {'hit_rate': 0.0, 'hits': 0, 'misses': 0}
    
    def get_average_response_time(self) -> float:
        """Obtém tempo médio de resposta das últimas requisições"""
        try:
            # Busca no Redis as últimas métricas de resposta
            response_times = self.redis_client.lrange('response_times', 0, 99)
            if response_times:
                times = [float(t) for t in response_times]
                return sum(times) / len(times)
            return 0.0
        except:
            return 0.0
    
    def get_error_rate(self) -> float:
        """Obtém taxa de erro das últimas requisições"""
        try:
            total_requests = self.redis_client.get('total_requests_last_hour') or 0
            error_requests = self.redis_client.get('error_requests_last_hour') or 0
            
            total = int(total_requests)
            errors = int(error_requests)
            
            return (errors / total * 100) if total > 0 else 0.0
        except:
            return 0.0
    
    def get_active_users_count(self, minutes: int = 5) -> int:
        """Conta usuários ativos nos últimos N minutos"""
        try:
            # Busca sessões ativas no Redis
            active_sessions = self.redis_client.keys('session:*')
            return len(active_sessions)
        except:
            return 0
    
    def get_new_registrations_count(self, hours: int = 1) -> int:
        """Conta novos registros nas últimas N horas"""
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            return User.objects.filter(date_joined__gte=cutoff).count()
        except:
            return 0
    
    def get_sessions_started_count(self, hours: int = 1) -> int:
        """Conta sessões iniciadas nas últimas N horas"""
        try:
            # Implementar baseado em logs ou modelo de sessão
            return self.redis_client.get(f'sessions_started_last_{hours}h') or 0
        except:
            return 0
    
    def get_questions_answered_count(self, hours: int = 1) -> int:
        """Conta questões respondidas nas últimas N horas"""
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            from questions.models import UserAnswer
            return UserAnswer.objects.filter(answered_at__gte=cutoff).count()
        except:
            return 0
    
    def get_lessons_completed_count(self, hours: int = 1) -> int:
        """Conta lições completadas nas últimas N horas"""
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            from courses.models import UserLesson
            return UserLesson.objects.filter(
                completed_at__gte=cutoff,
                is_completed=True
            ).count()
        except:
            return 0
    
    def get_achievements_unlocked_count(self, hours: int = 1) -> int:
        """Conta conquistas desbloqueadas nas últimas N horas"""
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            from gamification.models import UserAchievement
            return UserAchievement.objects.filter(unlocked_at__gte=cutoff).count()
        except:
            return 0
    
    def get_revenue_generated(self, hours: int = 1) -> float:
        """Obtém receita gerada nas últimas N horas"""
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            from gamification.models import UserPurchase
            purchases = UserPurchase.objects.filter(purchased_at__gte=cutoff)
            return sum(p.price for p in purchases)
        except:
            return 0.0
    
    def get_slow_queries(self) -> List[Dict]:
        """Obtém consultas lentas do banco"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT query, mean_time, calls, total_time
                    FROM pg_stat_statements 
                    WHERE mean_time > 1000 
                    ORDER BY mean_time DESC 
                    LIMIT 10;
                """)
                return [
                    {
                        'query': row[0][:100],
                        'mean_time': row[1],
                        'calls': row[2],
                        'total_time': row[3]
                    }
                    for row in cursor.fetchall()
                ]
        except:
            return []
    
    def get_database_locks(self) -> List[Dict]:
        """Obtém bloqueios ativos do banco"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT locktype, database, relation, page, tuple, 
                           virtualxid, transactionid, mode, granted
                    FROM pg_locks 
                    WHERE NOT granted;
                """)
                return [
                    {
                        'locktype': row[0],
                        'database': row[1],
                        'mode': row[6],
                        'granted': row[8]
                    }
                    for row in cursor.fetchall()
                ]
        except:
            return []
    
    def get_database_size(self) -> float:
        """Obtém tamanho do banco em MB"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database()));
                """)
                size_str = cursor.fetchone()[0]
                # Parse do tamanho (aproximado)
                if 'MB' in size_str:
                    return float(size_str.replace(' MB', ''))
                elif 'GB' in size_str:
                    return float(size_str.replace(' GB', '')) * 1024
                return 0.0
        except:
            return 0.0
    
    def get_unused_indexes(self) -> List[Dict]:
        """Obtém índices não utilizados"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
                    FROM pg_stat_user_indexes 
                    WHERE idx_tup_read = 0 AND idx_tup_fetch = 0;
                """)
                return [
                    {
                        'schema': row[0],
                        'table': row[1],
                        'index': row[2]
                    }
                    for row in cursor.fetchall()
                ]
        except:
            return []
    
    def get_top_endpoints(self) -> List[Dict]:
        """Obtém endpoints mais utilizados"""
        try:
            # Busca do Redis métricas de endpoints
            endpoints_data = self.redis_client.hgetall('endpoint_usage')
            return [
                {'endpoint': k.decode(), 'count': int(v)}
                for k, v in endpoints_data.items()
            ][:10]
        except:
            return []
    
    def get_slow_endpoints(self) -> List[Dict]:
        """Obtém endpoints com maior latência"""
        try:
            # Busca do Redis métricas de latência
            endpoints_data = self.redis_client.hgetall('endpoint_latency')
            return [
                {'endpoint': k.decode(), 'avg_latency': float(v)}
                for k, v in endpoints_data.items()
            ][:10]
        except:
            return []
    
    def get_endpoint_error_rates(self) -> Dict[str, float]:
        """Obtém taxa de erro por endpoint"""
        try:
            error_data = self.redis_client.hgetall('endpoint_errors')
            usage_data = self.redis_client.hgetall('endpoint_usage')
            
            error_rates = {}
            for endpoint, errors in error_data.items():
                endpoint = endpoint.decode()
                errors = int(errors)
                usage = int(usage_data.get(endpoint.encode(), 0))
                
                if usage > 0:
                    error_rates[endpoint] = (errors / usage) * 100
            
            return error_rates
        except:
            return {}
    
    def store_metrics_in_redis(self, key: str, metrics):
        """Armazena métricas no Redis"""
        try:
            self.redis_client.lpush(
                f'metrics:{key}',
                json.dumps(asdict(metrics), default=str)
            )
            # Mantém apenas os últimos 1000 registros
            self.redis_client.ltrim(f'metrics:{key}', 0, 999)
        except Exception as e:
            self.logger.error(f"Error storing metrics in Redis: {e}")
    
    async def broadcast_metrics(self, metric_type: str, data: Dict):
        """Envia métricas via WebSocket"""
        if self.channel_layer:
            try:
                await self.channel_layer.group_send(
                    'monitoring_dashboard',
                    {
                        'type': 'send_metrics',
                        'metric_type': metric_type,
                        'data': data
                    }
                )
            except Exception as e:
                self.logger.error(f"Error broadcasting metrics: {e}")
    
    async def broadcast_alert(self, alert: Alert):
        """Envia alerta via WebSocket"""
        if self.channel_layer:
            try:
                await self.channel_layer.group_send(
                    'monitoring_dashboard',
                    {
                        'type': 'send_alert',
                        'alert': asdict(alert)
                    }
                )
            except Exception as e:
                self.logger.error(f"Error broadcasting alert: {e}")
    
    async def broadcast_alert_resolved(self, alert: Alert):
        """Envia notificação de alerta resolvido"""
        if self.channel_layer:
            try:
                await self.channel_layer.group_send(
                    'monitoring_dashboard',
                    {
                        'type': 'alert_resolved',
                        'alert': asdict(alert)
                    }
                )
            except Exception as e:
                self.logger.error(f"Error broadcasting alert resolution: {e}")

# Instância global do monitor
monitor = RealTimeMonitor()

# Funções de utilidade para uso externo
def start_monitoring():
    """Inicia o monitoramento (para usar em management command)"""
    return asyncio.run(monitor.start_monitoring())

def get_current_metrics() -> Dict[str, Any]:
    """Obtém métricas atuais do sistema"""
    return {
        'system': asdict(monitor.metrics_history[-1]) if monitor.metrics_history else None,
        'user_activity': asdict(monitor.user_activity_history[-1]) if monitor.user_activity_history else None,
        'active_alerts': [asdict(a) for a in monitor.alerts if not a.is_resolved],
        'resolved_alerts_today': [
            asdict(a) for a in monitor.alerts 
            if a.is_resolved and a.timestamp.date() == datetime.now().date()
        ]
    }

def get_metrics_history(metric_type: str, hours: int = 24) -> List[Dict]:
    """Obtém histórico de métricas"""
    cutoff = datetime.now() - timedelta(hours=hours)
    
    if metric_type == 'system':
        return [
            asdict(m) for m in monitor.metrics_history 
            if m.timestamp > cutoff
        ]
    elif metric_type == 'user_activity':
        return [
            asdict(m) for m in monitor.user_activity_history 
            if m.timestamp > cutoff
        ]
    
    return [] 