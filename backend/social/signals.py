"""
Signals para o sistema social
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import StudyGroup, StudyGroupMembership, UserFriendship

User = get_user_model()

# Signals básicos para evitar erro de import
# Será expandido conforme necessário


@receiver(post_save, sender=StudyGroupMembership)
def update_group_stats_on_join(sender, instance, created, **kwargs):
    """Atualiza estatísticas do grupo quando alguém entra"""
    if created:
        group = instance.group
        group.save()  # Trigger any stat calculations


@receiver(post_delete, sender=StudyGroupMembership)
def update_group_stats_on_leave(sender, instance, **kwargs):
    """Atualiza estatísticas do grupo quando alguém sai"""
    group = instance.group
    group.save()  # Trigger any stat calculations


@receiver(post_save, sender=UserFriendship)
def friendship_created(sender, instance, created, **kwargs):
    """Notifica quando uma amizade é criada"""
    if created and instance.status == 'accepted':
        # Aqui você pode adicionar lógica para notificações
        pass 