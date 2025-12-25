from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = 'Creates test users (admin and analyst) for API testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default='testpass123',
            help='Password for test users (default: testpass123)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing test users before creating new ones',
        )

    def handle(self, *args, **options):
        password = options['password']
        reset = options['reset']

        # Ensure groups exist
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        analyst_group, _ = Group.objects.get_or_create(name='Analyst')

        # Test users to create
        test_users = [
            {
                'username': 'admin',
                'email': 'admin@threatmonitor.local',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'groups': [admin_group],
            },
            {
                'username': 'analyst',
                'email': 'analyst@threatmonitor.local',
                'first_name': 'Analyst',
                'last_name': 'User',
                'is_staff': False,
                'is_superuser': False,
                'groups': [analyst_group],
            },
            {
                'username': 'testadmin',
                'email': 'testadmin@threatmonitor.local',
                'first_name': 'Test',
                'last_name': 'Admin',
                'is_staff': False,
                'is_superuser': False,
                'groups': [admin_group],
            },
            {
                'username': 'testanalyst',
                'email': 'testanalyst@threatmonitor.local',
                'first_name': 'Test',
                'last_name': 'Analyst',
                'is_staff': False,
                'is_superuser': False,
                'groups': [analyst_group],
            },
        ]

        # Delete existing test users if reset flag is set
        if reset:
            usernames = [user['username'] for user in test_users]
            deleted_count = User.objects.filter(username__in=usernames).delete()[0]
            if deleted_count > 0:
                self.stdout.write(
                    self.style.WARNING(f'Deleted {deleted_count} existing test user(s)')
                )

        # Create test users
        created_count = 0
        updated_count = 0

        for user_data in test_users:
            groups = user_data.pop('groups')
            username = user_data['username']

            user, created = User.objects.get_or_create(
                username=username,
                defaults=user_data
            )

            if created:
                user.set_password(password)
                user.save()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'[+] Created user: {username}')
                )
            else:
                # Update existing user
                for key, value in user_data.items():
                    setattr(user, key, value)
                user.set_password(password)
                user.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'[~] Updated user: {username}')
                )

            # Assign groups
            user.groups.set(groups)
            group_names = ', '.join([g.name for g in groups])
            self.stdout.write(f'  Groups: {group_names}')

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Test Users Created Successfully'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write('Credentials (all users use the same password):')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write('')
        self.stdout.write('Admin Users (can create events, manage alerts):')
        self.stdout.write('  - admin / testpass123')
        self.stdout.write('  - testadmin / testpass123')
        self.stdout.write('')
        self.stdout.write('Analyst Users (read-only alerts, cannot create events):')
        self.stdout.write('  - analyst / testpass123')
        self.stdout.write('  - testanalyst / testpass123')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Total: {created_count} created, {updated_count} updated'))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('You can now use these credentials in Postman!'))

