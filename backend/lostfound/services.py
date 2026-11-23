"""Mga patakaran ng claim: dito nakasulat kung paano nagbabago ang status ng item.

Unclaimed → (may nag-claim) → Pending → (inaprubahan) → Claimed
                                      → (ni-reject)   → Unclaimed
"""
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from .exceptions import Conflict
from .models import Claim, Item


def submit_claim(*, item_id, full_name, student_no):
    try:
        with transaction.atomic():
            try:
                item = Item.objects.select_for_update().get(pk=item_id)
            except Item.DoesNotExist:
                raise NotFound('This item does not exist or was removed.')
            if item.status != Item.Status.UNCLAIMED:
                raise Conflict('This item can no longer be claimed.')
            claim = Claim.objects.create(item=item, full_name=full_name, student_no=student_no)
            item.status = Item.Status.PENDING
            item.save(update_fields=['status'])
            return claim
    except IntegrityError:
        # Dalawang claim ang sabay na pumasok. Isa lang ang tinanggap ng database.
        raise Conflict('This item can no longer be claimed.')


def decide_claim(*, claim_id, user, decision, verified_name, verified_student_no, handover_photo):
    with transaction.atomic():
        try:
            claim = Claim.objects.select_for_update().select_related('item').get(pk=claim_id)
        except Claim.DoesNotExist:
            raise NotFound('This claim does not exist.')
        if claim.status != Claim.Status.PENDING:
            raise Conflict('This claim was already decided.')

        approving = decision == Claim.Status.APPROVED
        if approving and not handover_photo:
            raise ValidationError('Add the handover photo before approving.')

        claim.status = decision
        claim.verified_name = ' '.join(verified_name.split())
        claim.verified_student_no = verified_student_no.strip()
        claim.decided_at = timezone.now()
        claim.decided_by = user
        if approving:
            claim.handover_photo = handover_photo
        claim.save()

        item = claim.item
        item.status = Item.Status.CLAIMED if approving else Item.Status.UNCLAIMED
        item.save(update_fields=['status'])
        return claim
