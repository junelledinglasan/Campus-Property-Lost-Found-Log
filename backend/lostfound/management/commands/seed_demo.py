from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from lostfound.models import Category, Item

SAMPLE_ITEMS = [
    ('Black leather wallet', Category.WALLET, 'Folded wallet with a worn corner. Has a few cards inside.', 'Library, 2nd floor', 1),
    ('Blue umbrella with wooden handle', Category.OTHER, 'Large folding umbrella, navy blue, with a loop strap.', 'Canteen', 2),
    ('Scientific calculator', Category.BOOKS, 'Casio fx-991, name sticker peeled off the back.', 'Room 204', 3),
    ('Set of keys with green lanyard', Category.KEYS, 'Three keys on a green lanyard with a small bear keychain.', 'Main gate', 5),
    ('Gray hoodie, size M', Category.CLOTHING, 'Plain gray pullover hoodie, left on a bench.', 'Covered court', 6),
    ('White earbuds in charging case', Category.PHONE, 'White wireless earbuds with a clear case.', 'Computer lab 3', 9),
]


class Command(BaseCommand):
    help = 'Gumagawa ng demo na OSAS staff account at sample na found items. Para sa development lang.'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='osas')
        parser.add_argument('--password', default='osas123')

    def handle(self, *args, **options):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=options['username'],
            defaults={'is_staff': True, 'is_superuser': True, 'first_name': 'OSAS', 'last_name': 'Staff'},
        )
        if created:
            user.set_password(options['password'])
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Staff account created: {user.username} / {options["password"]}'))
        else:
            self.stdout.write(f'Staff account "{user.username}" already exists, left unchanged.')

        if Item.objects.exists():
            self.stdout.write('Items already exist, no sample items added.')
            return

        today = timezone.localdate()
        for name, category, description, place, days_ago in SAMPLE_ITEMS:
            Item.objects.create(
                name=name,
                category=category,
                description=description,
                place_found=place,
                date_found=today - timedelta(days=days_ago),
            )
        self.stdout.write(self.style.SUCCESS(f'{len(SAMPLE_ITEMS)} sample items added.'))
        self.stdout.write(self.style.WARNING('Ang demo password ay para sa development lang. Huwag gamitin sa production.'))
