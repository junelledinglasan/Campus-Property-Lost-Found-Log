from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from . import services
from .models import Claim, Item
from .permissions import IsStaff
from .serializers import (
    ClaimCreateSerializer,
    ClaimDecisionSerializer,
    ClaimSerializer,
    ItemSerializer,
)


class LoginThrottle(AnonRateThrottle):
    scope = 'login'


class ClaimSubmitThrottle(AnonRateThrottle):
    scope = 'claim_submit'


def display_name(user):
    return user.get_full_name() or user.get_username()


# ---------- Auth ----------

class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        username = str(request.data.get('username', '')).strip()
        password = str(request.data.get('password', ''))
        user = authenticate(request, username=username, password=password)
        # Iisang mensahe para sa maling username, maling password, at hindi-staff.
        if user is None or not user.is_staff:
            return Response({'detail': 'Wrong username or password.'}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {'username': user.get_username(), 'displayName': display_name(user)},
        })


class LogoutView(APIView):
    permission_classes = [IsStaff]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------- Items ----------

class ItemViewSet(viewsets.ModelViewSet):
    """Bukas sa lahat ang pagbasa. OSAS staff lang ang pwedeng mag-post, mag-edit, at magbura."""

    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsStaff()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Ang proof photo ay kasama lang sa detalye ng isang item, para hindi bumigat ang listahan.
        context['include_proof'] = self.action == 'retrieve'
        return context


# ---------- Claims ----------

class ClaimListCreateView(APIView):
    """GET: listahan ng claims (staff lang). POST: magsumite ng claim (bukas sa lahat)."""

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsStaff()]

    def get_throttles(self):
        if self.request.method == 'POST':
            return [ClaimSubmitThrottle()]
        return []

    def get(self, request):
        claims = Claim.objects.select_related('item', 'decided_by')
        return Response(ClaimSerializer(claims, many=True).data)

    def post(self, request):
        serializer = ClaimCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        claim = services.submit_claim(
            item_id=data['itemId'],
            full_name=data['fullName'],
            student_no=data['studentNo'],
        )
        # Walang ibinabalik na personal na detalye sa public na endpoint.
        return Response({'id': claim.id}, status=status.HTTP_201_CREATED)


class ClaimDecideView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, pk):
        serializer = ClaimDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        claim = services.decide_claim(
            claim_id=pk,
            user=request.user,
            decision=data['decision'],
            verified_name=data['verifiedName'],
            verified_student_no=data['verifiedStudentNo'],
            handover_photo=data.get('handoverPhoto'),
        )
        claim = Claim.objects.select_related('item', 'decided_by').get(pk=claim.pk)
        return Response(ClaimSerializer(claim).data)
