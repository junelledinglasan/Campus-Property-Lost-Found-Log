import re

from django.utils import timezone
from rest_framework import serializers

from .fields import Base64ImageField, HandoverPhotoField
from .models import Claim, Item

STUDENT_NO = re.compile(r'^[A-Za-z0-9-]{4,20}$')

# Ang mga pangalan ng field ay camelCase para tumugma sa frontend.


class ItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=120,
        error_messages={'blank': 'Enter the item name.', 'required': 'Enter the item name.'},
    )
    description = serializers.CharField(required=False, allow_blank=True)
    photo = Base64ImageField(required=False, allow_null=True)
    dateFound = serializers.DateField(
        source='date_found',
        error_messages={
            'required': 'Enter the date the item was found.',
            'invalid': 'Enter a valid date.',
            'null': 'Enter the date the item was found.',
        },
    )
    placeFound = serializers.CharField(
        source='place_found',
        max_length=120,
        error_messages={'blank': 'Enter where the item was found.', 'required': 'Enter where the item was found.'},
    )
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    # Proof na naibalik na ang item: ang handover photo ng inaprubahang claim. Makikita ng lahat,
    # pero sa detalye lang ng isang item (hindi sa listahan), at walang pangalan o student number.
    handoverPhoto = serializers.SerializerMethodField()
    returnedAt = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ['id', 'name', 'category', 'description', 'photo', 'dateFound', 'placeFound', 'status', 'createdAt',
                  'handoverPhoto', 'returnedAt']
        # Hindi pwedeng baguhin ang status nang direkta. Nagbabago lang ito sa pamamagitan ng mga claim.
        read_only_fields = ['id', 'status']

    def _approved_claim(self, item):
        if item.status != Item.Status.CLAIMED:
            return None
        return item.claims.filter(status=Claim.Status.APPROVED).order_by('-decided_at', '-id').first()

    def get_handoverPhoto(self, item):  # noqa: N802
        if not self.context.get('include_proof'):
            return None
        claim = self._approved_claim(item)
        return HandoverPhotoField().to_representation(claim.handover_photo) if claim else None

    def get_returnedAt(self, item):  # noqa: N802
        if not self.context.get('include_proof'):
            return None
        claim = self._approved_claim(item)
        return claim.decided_at.isoformat() if claim and claim.decided_at else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not self.context.get('include_proof'):
            data.pop('handoverPhoto', None)
            data.pop('returnedAt', None)
        return data

    def validate_dateFound(self, value):  # noqa: N802 (sinusunod ang pangalan ng field)
        if value > timezone.localdate():
            raise serializers.ValidationError('The date found cannot be in the future.')
        return value

    def update(self, instance, validated_data):
        old_name = instance.photo.name if instance.photo else None
        instance = super().update(instance, validated_data)
        new_name = instance.photo.name if instance.photo else None
        if 'photo' in validated_data and old_name and old_name != new_name:
            instance.photo.storage.delete(old_name)
        return instance


class ClaimCreateSerializer(serializers.Serializer):
    itemId = serializers.IntegerField()
    fullName = serializers.CharField(
        max_length=120,
        error_messages={'blank': 'Enter your full name, first and last.', 'required': 'Enter your full name, first and last.'},
    )
    studentNo = serializers.CharField(
        max_length=20,
        error_messages={'blank': 'Enter your student number.', 'required': 'Enter your student number.'},
    )

    def validate_fullName(self, value):  # noqa: N802
        value = ' '.join(value.split())
        if len(value.split(' ')) < 2:
            raise serializers.ValidationError('Enter your full name, first and last.')
        return value

    def validate_studentNo(self, value):  # noqa: N802
        if not STUDENT_NO.match(value):
            raise serializers.ValidationError('Enter a valid student number (letters, numbers, and dashes only).')
        return value


class ClaimDecisionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(
        choices=[Claim.Status.APPROVED, Claim.Status.REJECTED],
        error_messages={'invalid_choice': 'Decision must be Approved or Rejected.'},
    )
    verifiedName = serializers.CharField(
        max_length=120,
        error_messages={'blank': 'Enter the name and student number shown on the ID.',
                        'required': 'Enter the name and student number shown on the ID.'},
    )
    verifiedStudentNo = serializers.CharField(
        max_length=20,
        error_messages={'blank': 'Enter the name and student number shown on the ID.',
                        'required': 'Enter the name and student number shown on the ID.'},
    )
    handoverPhoto = Base64ImageField(required=False, allow_null=True)


class ClaimSerializer(serializers.ModelSerializer):
    """Para sa staff lang. May personal na detalye at handover photo."""

    itemId = serializers.IntegerField(source='item_id', read_only=True)
    itemName = serializers.CharField(source='item.name', read_only=True)
    fullName = serializers.CharField(source='full_name', read_only=True)
    studentNo = serializers.CharField(source='student_no', read_only=True)
    submittedAt = serializers.DateTimeField(source='submitted_at', read_only=True)
    verifiedName = serializers.CharField(source='verified_name', read_only=True)
    verifiedStudentNo = serializers.CharField(source='verified_student_no', read_only=True)
    handoverPhoto = HandoverPhotoField(source='handover_photo', read_only=True)
    decidedAt = serializers.DateTimeField(source='decided_at', read_only=True)
    decidedBy = serializers.SerializerMethodField()

    class Meta:
        model = Claim
        fields = [
            'id', 'itemId', 'itemName', 'fullName', 'studentNo', 'submittedAt', 'status',
            'verifiedName', 'verifiedStudentNo', 'handoverPhoto', 'decidedAt', 'decidedBy',
        ]
        read_only_fields = fields

    def get_decidedBy(self, obj):  # noqa: N802
        if not obj.decided_by:
            return None
        return obj.decided_by.get_full_name() or obj.decided_by.get_username()
