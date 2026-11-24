"""Gumagawa ng OSAS staff account mula sa environment variable. Para ito sa deployment na walang shell
(hal. libreng plan ng Render), at ligtas patakbuhin nang paulit-ulit sa bawat deploy."""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Gumawa ng OSAS staff account kung wala pa, gamit ang OSAS_USERNAME at OSAS_PASSWORD.'

    def handle(self, *args, **options):
        username = os.environ.get('OSAS_USERNAME', '').strip()
        password = os.environ.get('OSAS_PASSWORD', '')
        if not username and not password:
            self.stdout.write('Walang OSAS_USERNAME at OSAS_PASSWORD, nilaktawan.')
            return
        if not username or not password:
            raise CommandError('I-set ang pareho: OSAS_USERNAME at OSAS_PASSWORD.')
        if len(password) < 8:
            raise CommandError('Dapat hindi bababa sa 8 character ang OSAS_PASSWORD.')

        User = get_user_model()
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Ginawa ang staff account na "{username}".'))
        else:
            # Hindi binabago ang password ng umiiral na account, para hindi ma-overwrite ang pinalitan na.
            self.stdout.write(f'Umiiral na ang "{username}", walang binago.')
