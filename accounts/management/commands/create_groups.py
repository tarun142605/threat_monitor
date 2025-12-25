from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Creates Admin and Analyst groups'

    def handle(self, *args, **options):
        admin_group, created = Group.objects.get_or_create(name='Admin')
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Admin group'))
        else:
            self.stdout.write(self.style.WARNING('Admin group already exists'))

        analyst_group, created = Group.objects.get_or_create(name='Analyst')
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created Analyst group'))
        else:
            self.stdout.write(self.style.WARNING('Analyst group already exists'))
