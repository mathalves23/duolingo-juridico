"""
Configuração do Celery para processamento assíncrono
"""

import os
from celery import Celery
from django.conf import settings

# Definir variável de ambiente padrão para Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Criar instância do Celery
app = Celery('duolingo_juridico')

# Configuração do Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configurações específicas
app.conf.update(
    # Broker (Redis recomendado para produção)
    broker_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    
    # Serializers
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='America/Sao_Paulo',
    enable_utc=True,
    
    # Configurações de worker
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Configurações de retry
    task_default_retry_delay=60,  # 1 minuto
    task_max_retries=3,
    
    # Rate limiting
    task_annotations={
        'integrations.api_integrations.process_ai_request': {
            'rate_limit': '10/m'  # 10 por minuto
        },
        'integrations.api_integrations.send_notification_batch': {
            'rate_limit': '100/h'  # 100 por hora
        },
    },
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Security
    worker_hijack_root_logger=False,
    worker_log_color=False,
)

# Descobrir tarefas automaticamente
app.autodiscover_tasks()

# Configuração de rotas para diferentes tipos de tarefas
app.conf.task_routes = {
    'integrations.api_integrations.process_ai_request': {'queue': 'ai_processing'},
    'integrations.api_integrations.send_notification_batch': {'queue': 'notifications'},
    'billing.tasks.*': {'queue': 'billing'},
    'video_learning.tasks.*': {'queue': 'media_processing'},
}

# Configuração de beat schedule para tarefas periódicas
app.conf.beat_schedule = {
    # Backup de dados críticos
    'backup-critical-data': {
        'task': 'core.tasks.backup_critical_data',
        'schedule': 3600.0,  # A cada hora
    },
    
    # Limpeza de cache
    'cleanup-cache': {
        'task': 'core.tasks.cleanup_expired_cache',
        'schedule': 1800.0,  # A cada 30 minutos
    },
    
    # Análise de performance
    'analyze-performance': {
        'task': 'analytics.tasks.analyze_system_performance',
        'schedule': 300.0,  # A cada 5 minutos
    },
    
    # Sincronização com APIs externas
    'sync-external-data': {
        'task': 'integrations.tasks.sync_external_apis',
        'schedule': 3600.0,  # A cada hora
    },
    
    # Processamento de métricas
    'process-metrics': {
        'task': 'analytics.tasks.process_daily_metrics',
        'schedule': 86400.0,  # Diário
    },
    
    # Verificação de saúde do sistema
    'health-check': {
        'task': 'core.tasks.system_health_check',
        'schedule': 300.0,  # A cada 5 minutos
    },
}

@app.task(bind=True)
def debug_task(self):
    """Tarefa de debug"""
    print(f'Request: {self.request!r}') 