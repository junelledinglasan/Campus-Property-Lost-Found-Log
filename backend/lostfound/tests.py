import base64
import io
import shutil
import tempfile
from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from django.utils import timezone
from PIL import Image
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.throttling import SimpleRateThrottle

from .models import Claim, Item

TMP_MEDIA = tempfile.mkdtemp(prefix='lf-media-')
TMP_PRIVATE = tempfile.mkdtemp(prefix='lf-private-')


def data_url(fmt='JPEG', size=(20, 20), color=(200, 30, 30)):
    buffer = io.BytesIO()
    Image.new('RGB', size, color).save(buffer, fmt)
    mime = {'JPEG': 'image/jpeg', 'PNG': 'image/png'}[fmt]
    return f'data:{mime};base64,{base64.b64encode(buffer.getvalue()).decode()}'


@override_settings(MEDIA_ROOT=TMP_MEDIA, PRIVATE_MEDIA_ROOT=TMP_PRIVATE)
class ApiTestCase(APITestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TMP_MEDIA, ignore_errors=True)
        shutil.rmtree(TMP_PRIVATE, ignore_errors=True)

    def setUp(self):
        cache.clear()  # para hindi maapektuhan ng throttle ang ibang test
        User = get_user_model()
        self.staff = User.objects.create_user('osas', password='osas123', is_staff=True, first_name='OSAS', last_name='Staff')
        self.student = User.objects.create_user('student', password='pw-student-123', is_staff=False)
        self.item = Item.objects.create(
            name='Black wallet', category='Wallet and cards', place_found='Library',
            date_found=timezone.localdate() - timedelta(days=1),
        )

    def sign_in(self, user=None):
        token, _ = Token.objects.get_or_create(user=user or self.staff)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def claim(self, item=None, name='Juan Dela Cruz', no='2022-00123'):
        return self.client.post('/api/claims/', {'itemId': (item or self.item).id, 'fullName': name, 'studentNo': no}, format='json')


class AuthTests(ApiTestCase):
    def test_staff_can_log_in(self):
        r = self.client.post('/api/auth/login/', {'username': 'osas', 'password': 'osas123'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data['token'])
        self.assertEqual(r.data['user'], {'username': 'osas', 'displayName': 'OSAS Staff'})

    def test_wrong_password_and_non_staff_get_same_message(self):
        a = self.client.post('/api/auth/login/', {'username': 'osas', 'password': 'nope'}, format='json')
        b = self.client.post('/api/auth/login/', {'username': 'student', 'password': 'pw-student-123'}, format='json')
        self.assertEqual(a.status_code, 400)
        self.assertEqual(b.status_code, 400)
        self.assertEqual(a.data, b.data)
        self.assertEqual(a.data['detail'], 'Wrong username or password.')

    def test_login_is_throttled(self):
        for _ in range(10):
            self.client.post('/api/auth/login/', {'username': 'osas', 'password': 'bad'}, format='json')
        r = self.client.post('/api/auth/login/', {'username': 'osas', 'password': 'bad'}, format='json')
        self.assertEqual(r.status_code, 429)

    def test_logout_deletes_token(self):
        self.sign_in()
        self.assertEqual(self.client.post('/api/auth/logout/').status_code, 204)
        self.assertFalse(Token.objects.filter(user=self.staff).exists())

    def test_stale_token_does_not_break_public_browsing(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token stale-token')
        self.assertEqual(self.client.get('/api/items/').status_code, 200)
        r = self.client.get('/api/claims/')
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.data['detail'], 'Sign in as OSAS staff to do this.')


class ItemTests(ApiTestCase):
    def test_public_can_list_and_read_items(self):
        r = self.client.get('/api/items/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(set(r.data[0]), {'id', 'name', 'category', 'description', 'photo', 'dateFound', 'placeFound', 'status', 'createdAt'})
        self.assertEqual(self.client.get(f'/api/items/{self.item.id}/').status_code, 200)

    def test_missing_item_message(self):
        r = self.client.get('/api/items/9999/')
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.data['detail'], 'This item does not exist or was removed.')

    def test_only_staff_can_write(self):
        body = {'name': 'Umbrella', 'category': 'Other', 'dateFound': str(timezone.localdate()), 'placeFound': 'Canteen'}
        self.assertEqual(self.client.post('/api/items/', body, format='json').status_code, 401)
        self.sign_in(self.student)  # may token pero hindi staff
        self.assertEqual(self.client.post('/api/items/', body, format='json').status_code, 403)
        self.assertEqual(self.client.delete(f'/api/items/{self.item.id}/').status_code, 403)

    def test_staff_creates_item_with_photo(self):
        self.sign_in()
        body = {'name': 'Umbrella', 'category': 'Other', 'dateFound': str(timezone.localdate()),
                'placeFound': 'Canteen', 'photo': data_url()}
        r = self.client.post('/api/items/', body, format='json')
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data['status'], 'Unclaimed')
        self.assertTrue(r.data['photo'].startswith('/media/items/'))

    def test_status_cannot_be_set_directly(self):
        self.sign_in()
        r = self.client.patch(f'/api/items/{self.item.id}/', {'status': 'Claimed'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, 'Unclaimed')

    def test_validation_messages(self):
        self.sign_in()
        future = str(timezone.localdate() + timedelta(days=2))
        r = self.client.post('/api/items/', {'name': '  ', 'category': 'Other', 'dateFound': future, 'placeFound': 'X'}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data['detail'], 'Enter the item name.')
        r = self.client.post('/api/items/', {'name': 'A', 'category': 'Other', 'dateFound': future, 'placeFound': 'X'}, format='json')
        self.assertEqual(r.data['detail'], 'The date found cannot be in the future.')
        r = self.client.post('/api/items/', {'name': 'A', 'category': 'Nope', 'dateFound': str(timezone.localdate()), 'placeFound': 'X'}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_rejects_non_image_and_oversized_photo(self):
        self.sign_in()
        base = {'name': 'A', 'category': 'Other', 'dateFound': str(timezone.localdate()), 'placeFound': 'X'}
        fake = 'data:image/jpeg;base64,' + base64.b64encode(b'this is not an image').decode()
        r = self.client.post('/api/items/', {**base, 'photo': fake}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertIn('not a readable image', r.data['detail'])
        r = self.client.post('/api/items/', {**base, 'photo': 'data:text/html;base64,PGI+'}, format='json')
        self.assertEqual(r.status_code, 400)

    def test_edit_keeps_photo_when_frontend_sends_back_url(self):
        self.sign_in()
        body = {'name': 'Bag', 'category': 'Bag', 'dateFound': str(timezone.localdate()), 'placeFound': 'Gym', 'photo': data_url()}
        created = self.client.post('/api/items/', body, format='json').data
        edited = {**body, 'name': 'Blue bag', 'photo': created['photo']}  # URL ng kasalukuyang larawan
        r = self.client.put(f'/api/items/{created["id"]}/', edited, format='json')
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data['photo'], created['photo'])
        r = self.client.put(f'/api/items/{created["id"]}/', {**edited, 'photo': None}, format='json')
        self.assertIsNone(r.data['photo'])

    def test_deleting_item_removes_its_claims(self):
        self.claim()
        self.sign_in()
        self.assertEqual(self.client.delete(f'/api/items/{self.item.id}/').status_code, 204)
        self.assertEqual(Claim.objects.count(), 0)


class ClaimFlowTests(ApiTestCase):
    def test_submit_claim_marks_item_pending_and_returns_no_personal_data(self):
        r = self.claim()
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(set(r.data), {'id'})
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, 'Pending')
        public = self.client.get(f'/api/items/{self.item.id}/').content.decode()
        self.assertNotIn('Juan', public)
        self.assertNotIn('2022-00123', public)

    def test_second_claim_on_same_item_is_refused(self):
        self.claim()
        r = self.claim(name='Maria Santos', no='2021-00456')
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.data['detail'], 'This item can no longer be claimed.')
        self.assertEqual(Claim.objects.count(), 1)

    def test_claim_validation(self):
        self.assertEqual(self.claim(name='Juan').data['detail'], 'Enter your full name, first and last.')
        self.assertIn('valid student number', self.claim(no='12').data['detail'])
        self.assertIn('valid student number', self.claim(no='<script>1</script>').data['detail'])
        r = self.client.post('/api/claims/', {'itemId': 9999, 'fullName': 'Juan Dela Cruz', 'studentNo': '2022-1'}, format='json')
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.data['detail'], 'This item does not exist or was removed.')

    def test_claim_list_is_staff_only(self):
        self.claim()
        self.assertEqual(self.client.get('/api/claims/').status_code, 401)
        self.sign_in(self.student)
        self.assertEqual(self.client.get('/api/claims/').status_code, 403)
        self.sign_in()
        r = self.client.get('/api/claims/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data[0]['fullName'], 'Juan Dela Cruz')
        self.assertEqual(r.data[0]['itemName'], 'Black wallet')

    def test_claim_submission_is_throttled(self):
        statuses = []
        # Pansamantalang 3 kada oras lang. Awtomatikong ibabalik pagkatapos ng with block.
        with mock.patch.object(SimpleRateThrottle, 'THROTTLE_RATES', {'claim_submit': '3/hour', 'login': '10/min'}):
            for i in range(5):
                other = Item.objects.create(name=f'x{i}', place_found='y', date_found=timezone.localdate())
                statuses.append(self.claim(item=other).status_code)
        self.assertEqual(statuses[:3], [201, 201, 201])
        self.assertEqual(statuses[3], 429)

    def decide(self, claim_id, **kw):
        body = {'decision': 'Approved', 'verifiedName': 'Juan Dela Cruz', 'verifiedStudentNo': '2022-00123',
                'handoverPhoto': data_url('PNG')}
        body.update(kw)
        return self.client.post(f'/api/claims/{claim_id}/decide/', body, format='json')

    def test_decide_requires_staff(self):
        cid = self.claim().data['id']
        self.assertEqual(self.decide(cid).status_code, 401)
        self.sign_in(self.student)
        self.assertEqual(self.decide(cid).status_code, 403)

    def test_approve_requires_photo_and_marks_claimed(self):
        cid = self.claim().data['id']
        self.sign_in()
        r = self.decide(cid, handoverPhoto=None)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data['detail'], 'Add the handover photo before approving.')
        r = self.decide(cid)
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data['status'], 'Approved')
        self.assertEqual(r.data['decidedBy'], 'OSAS Staff')
        self.assertTrue(r.data['handoverPhoto'].startswith('data:image/png;base64,'))
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, 'Claimed')
        # Hindi na pwedeng i-decide ulit o i-claim ulit
        self.assertEqual(self.decide(cid).status_code, 409)
        self.client.credentials()
        self.assertEqual(self.claim().status_code, 409)

    def test_verified_details_are_saved_as_checked_on_id(self):
        cid = self.claim().data['id']
        self.sign_in()
        r = self.decide(cid, verifiedName='  Juan   P.  Dela Cruz ', verifiedStudentNo=' 2022-00124 ')
        self.assertEqual(r.data['verifiedName'], 'Juan P. Dela Cruz')
        self.assertEqual(r.data['verifiedStudentNo'], '2022-00124')
        self.assertEqual(r.data['studentNo'], '2022-00123')  # nananatili ang isinumite

    def test_reject_makes_item_available_again(self):
        cid = self.claim().data['id']
        self.sign_in()
        r = self.decide(cid, decision='Rejected', handoverPhoto=None)
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data['status'], 'Rejected')
        self.assertIsNone(r.data['handoverPhoto'])
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, 'Unclaimed')
        self.client.credentials()
        self.assertEqual(self.claim(name='Maria Santos', no='2021-00456').status_code, 201)

    def test_decide_validation(self):
        cid = self.claim().data['id']
        self.sign_in()
        self.assertEqual(self.decide(cid, decision='Maybe').status_code, 400)
        r = self.decide(cid, verifiedName='')
        self.assertEqual(r.data['detail'], 'Enter the name and student number shown on the ID.')
        self.assertEqual(self.decide(9999).status_code, 404)

    def test_handover_photo_is_not_publicly_served(self):
        cid = self.claim().data['id']
        self.sign_in()
        self.decide(cid)
        claim = Claim.objects.get(pk=cid)
        self.assertNotIn(TMP_MEDIA, claim.handover_photo.path)
        self.assertIn(TMP_PRIVATE, claim.handover_photo.path)
