from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class LenientTokenAuthentication(TokenAuthentication):
    """Kapag luma o mali ang token, ituturing na anonymous ang user, hindi error.

    Kung hindi, masisira ang pag-browse at pag-claim ng estudyante dahil lang sa lumang token
    na naiwan sa browser. Ang mga endpoint na para sa staff ay magbabalik pa rin ng 401.
    """

    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except AuthenticationFailed:
            return None
