"""Binubura ang mga file ng larawan kapag binura ang record, para hindi mag-iwan ng basura sa disk."""
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Claim, Item


@receiver(post_delete, sender=Item)
def delete_item_photo(sender, instance, **kwargs):
    if instance.photo:
        instance.photo.delete(save=False)


@receiver(post_delete, sender=Claim)
def delete_handover_photo(sender, instance, **kwargs):
    if instance.handover_photo:
        instance.handover_photo.delete(save=False)
