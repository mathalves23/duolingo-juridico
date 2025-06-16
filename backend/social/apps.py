from django.apps import AppConfig


class SocialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social'
    verbose_name = 'Sistema Social'
    
    def ready(self):
        # Comentando temporariamente até criar o arquivo signals.py
        # import social.signals 
        pass 