"""
Sistema de otimização de performance e caching
"""

import time
import functools
import logging
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from django.core.cache import cache
from django.core.cache.backends.redis import RedisCache
from django.db import connection
from django.conf import settings
import redis
import hashlib
import pickle
import asyncio
from concurrent.futures import ThreadPoolExecutor
import psutil
import gc
from django.db.models import QuerySet
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# Configuração do Redis para cache distribuído
redis_client = redis.Redis.from_url(
    settings.CACHES['default']['LOCATION'],
    decode_responses=False
)

class PerformanceMonitor:
    """Monitor de performance do sistema"""
    
    def __init__(self):
        self.metrics = {}
        self.thresholds = {
            'response_time': 2.0,  # segundos
            'memory_usage': 80,    # porcentagem
            'cpu_usage': 75,       # porcentagem
            'db_queries': 50,      # número máximo por request
        }
    
    def start_request_monitoring(self, request_id: str):
        """Iniciar monitoramento de requisição"""
        self.metrics[request_id] = {
            'start_time': time.time(),
            'db_queries_count': len(connection.queries),
            'memory_start': psutil.Process().memory_info().rss / 1024 / 1024,  # MB
        }
    
    def end_request_monitoring(self, request_id: str) -> Dict:
        """Finalizar monitoramento e retornar métricas"""
        if request_id not in self.metrics:
            return {}
        
        start_metrics = self.metrics[request_id]
        end_time = time.time()
        
        metrics = {
            'request_id': request_id,
            'response_time': end_time - start_metrics['start_time'],
            'db_queries': len(connection.queries) - start_metrics['db_queries_count'],
            'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024,
            'memory_delta': psutil.Process().memory_info().rss / 1024 / 1024 - start_metrics['memory_start'],
            'cpu_percent': psutil.cpu_percent(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Verificar se excedeu limites
        metrics['alerts'] = []
        if metrics['response_time'] > self.thresholds['response_time']:
            metrics['alerts'].append(f"Response time exceeded: {metrics['response_time']:.2f}s")
        
        if metrics['db_queries'] > self.thresholds['db_queries']:
            metrics['alerts'].append(f"Too many DB queries: {metrics['db_queries']}")
        
        if metrics['cpu_percent'] > self.thresholds['cpu_usage']:
            metrics['alerts'].append(f"High CPU usage: {metrics['cpu_percent']:.1f}%")
        
        # Limpar metrics antigos
        del self.metrics[request_id]
        
        # Log se houver alertas
        if metrics['alerts']:
            logger.warning(f"Performance alerts for {request_id}: {metrics['alerts']}")
        
        return metrics
    
    def get_system_stats(self) -> Dict:
        """Obter estatísticas do sistema"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'total': psutil.virtual_memory().total / 1024 / 1024,  # MB
                'available': psutil.virtual_memory().available / 1024 / 1024,
                'percent': psutil.virtual_memory().percent,
            },
            'disk': {
                'total': psutil.disk_usage('/').total / 1024 / 1024 / 1024,  # GB
                'free': psutil.disk_usage('/').free / 1024 / 1024 / 1024,
                'percent': psutil.disk_usage('/').percent,
            },
            'active_connections': len(connection.queries),
            'cache_stats': self._get_cache_stats(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_cache_stats(self) -> Dict:
        """Obter estatísticas do cache Redis"""
        try:
            info = redis_client.info()
            return {
                'used_memory': info.get('used_memory', 0) / 1024 / 1024,  # MB
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': info.get('keyspace_hits', 0) / max(1, 
                    info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0)) * 100
            }
        except:
            return {}


class AdvancedCache:
    """Sistema de cache avançado com múltiplas camadas"""
    
    def __init__(self):
        self.local_cache = {}  # Cache em memória local
        self.redis_cache = redis_client
        self.default_timeout = 3600  # 1 hora
        self.max_local_cache_size = 1000
    
    def _generate_key(self, namespace: str, *args, **kwargs) -> str:
        """Gerar chave única para cache"""
        key_data = f"{namespace}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, namespace: str, *args, **kwargs) -> Any:
        """Obter valor do cache (local primeiro, depois Redis)"""
        key = self._generate_key(namespace, *args, **kwargs)
        
        # Verificar cache local primeiro
        if key in self.local_cache:
            data, expiry = self.local_cache[key]
            if datetime.now() < expiry:
                return data
            else:
                del self.local_cache[key]
        
        # Verificar Redis
        try:
            cached_data = self.redis_cache.get(key)
            if cached_data:
                data = pickle.loads(cached_data)
                # Armazenar no cache local também
                self._set_local_cache(key, data, 300)  # 5 minutos local
                return data
        except Exception as e:
            logger.error(f"Redis cache error: {e}")
        
        return None
    
    def set(self, namespace: str, value: Any, timeout: int = None, *args, **kwargs):
        """Definir valor no cache"""
        key = self._generate_key(namespace, *args, **kwargs)
        timeout = timeout or self.default_timeout
        
        # Cache local
        self._set_local_cache(key, value, min(timeout, 300))
        
        # Cache Redis
        try:
            serialized_data = pickle.dumps(value)
            self.redis_cache.setex(key, timeout, serialized_data)
        except Exception as e:
            logger.error(f"Redis cache set error: {e}")
    
    def _set_local_cache(self, key: str, value: Any, timeout: int):
        """Definir cache local com limite de tamanho"""
        # Limitar tamanho do cache local
        if len(self.local_cache) >= self.max_local_cache_size:
            # Remover item mais antigo
            oldest_key = min(self.local_cache.keys(), 
                           key=lambda k: self.local_cache[k][1])
            del self.local_cache[oldest_key]
        
        expiry = datetime.now() + timedelta(seconds=timeout)
        self.local_cache[key] = (value, expiry)
    
    def delete(self, namespace: str, *args, **kwargs):
        """Remover do cache"""
        key = self._generate_key(namespace, *args, **kwargs)
        
        # Remover do cache local
        self.local_cache.pop(key, None)
        
        # Remover do Redis
        try:
            self.redis_cache.delete(key)
        except Exception as e:
            logger.error(f"Redis cache delete error: {e}")
    
    def clear_namespace(self, namespace: str):
        """Limpar todo um namespace"""
        try:
            pattern = f"{namespace}:*"
            keys = self.redis_cache.keys(pattern)
            if keys:
                self.redis_cache.delete(*keys)
            
            # Limpar cache local também
            local_keys_to_remove = [k for k in self.local_cache.keys() if k.startswith(namespace)]
            for key in local_keys_to_remove:
                del self.local_cache[key]
                
        except Exception as e:
            logger.error(f"Cache clear error: {e}")


class QuerysetOptimizer:
    """Otimizador de querysets do Django"""
    
    @staticmethod
    def optimize_queryset(queryset: QuerySet) -> QuerySet:
        """Otimizar queryset automaticamente"""
        # Detectar relacionamentos frequentemente usados
        model = queryset.model
        
        # Lista de campos para select_related (ForeignKey, OneToOne)
        select_related_fields = []
        # Lista de campos para prefetch_related (ManyToMany, reverse ForeignKey)
        prefetch_related_fields = []
        
        for field in model._meta.get_fields():
            if hasattr(field, 'related_model') and field.related_model:
                if field.many_to_one or field.one_to_one:
                    select_related_fields.append(field.name)
                elif field.many_to_many or field.one_to_many:
                    prefetch_related_fields.append(field.name)
        
        # Aplicar otimizações
        if select_related_fields:
            queryset = queryset.select_related(*select_related_fields[:5])  # Limitar a 5
        
        if prefetch_related_fields:
            queryset = queryset.prefetch_related(*prefetch_related_fields[:3])  # Limitar a 3
        
        return queryset
    
    @staticmethod
    def analyze_query_performance(queryset: QuerySet) -> Dict:
        """Analisar performance de uma query"""
        import time
        from django.db import connection
        
        # Contar queries antes
        queries_before = len(connection.queries)
        
        # Executar query
        start_time = time.time()
        list(queryset)  # Force evaluation
        end_time = time.time()
        
        # Analisar resultado
        queries_after = len(connection.queries)
        
        return {
            'execution_time': end_time - start_time,
            'queries_count': queries_after - queries_before,
            'last_query': connection.queries[-1] if connection.queries else None,
            'queryset_str': str(queryset.query),
            'model': queryset.model.__name__,
            'count': queryset.count()
        }


class DatabaseOptimizer:
    """Otimizador de banco de dados"""
    
    @staticmethod
    def create_missing_indices():
        """Criar índices faltantes baseado em queries frequentes"""
        from django.db import connection
        
        # Índices recomendados baseados no uso
        recommended_indices = [
            "CREATE INDEX IF NOT EXISTS idx_user_answers_created_at ON questions_useranswer(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_user_answers_user_correct ON questions_useranswer(user_id, is_correct);",
            "CREATE INDEX IF NOT EXISTS idx_questions_subject_difficulty ON questions_question(subject_id, difficulty_level);",
            "CREATE INDEX IF NOT EXISTS idx_achievements_user_earned ON gamification_userachievement(user_id, earned_at);",
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_completed ON ai_service_adaptivelearningsession(user_id, is_completed);",
        ]
        
        with connection.cursor() as cursor:
            for index_sql in recommended_indices:
                try:
                    cursor.execute(index_sql)
                    logger.info(f"Created index: {index_sql}")
                except Exception as e:
                    logger.warning(f"Failed to create index: {e}")
    
    @staticmethod
    def analyze_slow_queries() -> List[Dict]:
        """Analisar queries lentas"""
        from django.db import connection
        
        # Buscar queries que demoram mais de 1 segundo
        slow_queries = []
        
        for query in connection.queries:
            if float(query['time']) > 1.0:
                slow_queries.append({
                    'sql': query['sql'],
                    'time': float(query['time']),
                    'timestamp': datetime.now().isoformat()
                })
        
        return sorted(slow_queries, key=lambda x: x['time'], reverse=True)


# Decoradores para cache automático
def cache_result(namespace: str, timeout: int = 3600):
    """Decorator para cache automático de resultados"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = AdvancedCache()
            
            # Tentar obter do cache
            result = cache_manager.get(namespace, *args, **kwargs)
            if result is not None:
                return result
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            cache_manager.set(namespace, result, timeout, *args, **kwargs)
            
            return result
        return wrapper
    return decorator


def performance_monitor(func):
    """Decorator para monitoramento de performance"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        monitor = PerformanceMonitor()
        request_id = f"{func.__name__}_{int(time.time() * 1000)}"
        
        monitor.start_request_monitoring(request_id)
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            metrics = monitor.end_request_monitoring(request_id)
            
            # Log métricas se necessário
            if metrics.get('alerts'):
                logger.warning(f"Performance issues in {func.__name__}: {metrics}")
    
    return wrapper


class AsyncTaskManager:
    """Gerenciador de tarefas assíncronas para otimização"""
    
    def __init__(self, max_workers: int = 10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_tasks = {}
    
    async def run_async(self, func: Callable, *args, **kwargs) -> Any:
        """Executar função de forma assíncrona"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args, **kwargs)
    
    def run_background_task(self, task_id: str, func: Callable, *args, **kwargs):
        """Executar tarefa em background"""
        future = self.executor.submit(func, *args, **kwargs)
        self.running_tasks[task_id] = future
        return task_id
    
    def get_task_result(self, task_id: str) -> Any:
        """Obter resultado de tarefa em background"""
        if task_id in self.running_tasks:
            future = self.running_tasks[task_id]
            if future.done():
                result = future.result()
                del self.running_tasks[task_id]
                return result
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancelar tarefa em background"""
        if task_id in self.running_tasks:
            future = self.running_tasks[task_id]
            cancelled = future.cancel()
            if cancelled:
                del self.running_tasks[task_id]
            return cancelled
        return False


# Instâncias globais
performance_monitor_instance = PerformanceMonitor()
cache_manager = AdvancedCache()
task_manager = AsyncTaskManager()

# Middleware para monitoramento automático
class PerformanceMiddleware:
    """Middleware para monitoramento automático de performance"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request_id = f"{request.method}_{request.path}_{int(time.time() * 1000)}"
        
        # Iniciar monitoramento
        performance_monitor_instance.start_request_monitoring(request_id)
        
        response = self.get_response(request)
        
        # Finalizar monitoramento
        metrics = performance_monitor_instance.end_request_monitoring(request_id)
        
        # Adicionar headers de performance
        if metrics:
            response['X-Response-Time'] = f"{metrics['response_time']:.3f}s"
            response['X-DB-Queries'] = str(metrics['db_queries'])
            response['X-Memory-Usage'] = f"{metrics['memory_usage']:.1f}MB"
        
        return response


# Signals para invalidação automática de cache
@receiver([post_save, post_delete])
def invalidate_related_cache(sender, instance, **kwargs):
    """Invalidar cache relacionado quando modelos são alterados"""
    
    # Mapear modelos para namespaces de cache
    cache_mappings = {
        'User': ['user_profile', 'user_stats', 'leaderboard'],
        'Question': ['questions', 'subject_questions'],
        'UserAnswer': ['user_progress', 'performance_stats'],
        'Achievement': ['achievements', 'user_achievements'],
        'LearningProfile': ['learning_analytics', 'recommendations'],
    }
    
    model_name = sender.__name__
    if model_name in cache_mappings:
        for namespace in cache_mappings[model_name]:
            cache_manager.clear_namespace(namespace)
            logger.info(f"Cleared cache namespace: {namespace}")


# Função para limpeza automática de cache
def cleanup_expired_cache():
    """Limpar cache expirado automaticamente"""
    try:
        # Limpar cache local
        current_time = datetime.now()
        expired_keys = [
            key for key, (_, expiry) in cache_manager.local_cache.items()
            if current_time >= expiry
        ]
        
        for key in expired_keys:
            del cache_manager.local_cache[key]
        
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        # Força garbage collection
        gc.collect()
        
    except Exception as e:
        logger.error(f"Cache cleanup error: {e}")


# Função para otimização automática
def auto_optimize_system():
    """Otimização automática do sistema"""
    try:
        # Criar índices faltantes
        DatabaseOptimizer.create_missing_indices()
        
        # Limpeza de cache
        cleanup_expired_cache()
        
        # Análise de queries lentas
        slow_queries = DatabaseOptimizer.analyze_slow_queries()
        if slow_queries:
            logger.warning(f"Found {len(slow_queries)} slow queries")
            for query in slow_queries[:5]:  # Log apenas as 5 mais lentas
                logger.warning(f"Slow query ({query['time']}s): {query['sql'][:200]}...")
        
        logger.info("System auto-optimization completed")
        
    except Exception as e:
        logger.error(f"Auto-optimization error: {e}") 