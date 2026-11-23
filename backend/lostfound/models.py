from django.conf import settings
from django.db import models
from django.db.models import Q

from .storage import private_storage


class Category(models.TextChoices):
    # Dapat magkapareho ang listahang ito at ang CATEGORIES sa frontend (src/api/mock.js at http.js).
    WALLET = 'Wallet and cards', 'Wallet and cards'
    ID_DOCS = 'ID and documents', 'ID and documents'
    BAG = 'Bag', 'Bag'
    PHONE = 'Phone and gadgets', 'Phone and gadgets'
    KEYS = 'Keys', 'Keys'
    CLOTHING = 'Clothing', 'Clothing'
    BOOKS = 'Books and school supplies', 'Books and school supplies'
    BOTTLE = 'Water bottle and tumbler', 'Water bottle and tumbler'
    OTHER = 'Other', 'Other'


class Item(models.Model):
    class Status(models.TextChoices):
        UNCLAIMED = 'Unclaimed'
        PENDING = 'Pending'
        CLAIMED = 'Claimed'

    name = models.CharField(max_length=120)
    category = models.CharField(max_length=40, choices=Category.choices, default=Category.OTHER)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='items/', blank=True, null=True)
    date_found = models.DateField()
    place_found = models.CharField(max_length=120)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UNCLAIMED, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_found', '-id']

    def __str__(self):
        return self.name


class Claim(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pending'
        APPROVED = 'Approved'
        REJECTED = 'Rejected'

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='claims')

    # Isinumite ng estudyante online
    full_name = models.CharField(max_length=120)
    student_no = models.CharField(max_length=20)
    submitted_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True)

    # Itinala ng OSAS mula sa ID ng kumuha
    verified_name = models.CharField(max_length=120, blank=True)
    verified_student_no = models.CharField(max_length=20, blank=True)
    handover_photo = models.ImageField(upload_to='handover/', storage=private_storage, blank=True, null=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='decided_claims',
    )

    class Meta:
        ordering = ['-submitted_at', '-id']
        constraints = [
            # Isang Pending claim lang kada item, ipinapatupad mismo ng database.
            models.UniqueConstraint(
                fields=['item'],
                condition=Q(status='Pending'),
                name='one_pending_claim_per_item',
            ),
        ]

    def __str__(self):
        return f'{self.full_name} → {self.item.name} ({self.status})'
