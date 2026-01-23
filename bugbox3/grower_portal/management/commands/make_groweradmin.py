from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from bugbox3.core.permissions import IS_GROWERADMIN

User = get_user_model()


class Command(BaseCommand):
    help = 'Make a user a grower admin (creates group, assigns permissions, adds user)'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user to make grower admin')

    def handle(self, *args, **options):
        username = options['username']

        self.stdout.write(self.style.SUCCESS(f'Making {username} a grower admin...\n'))

        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'Found user: {user.username} ({user.email})')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))
            self.stdout.write('\nAvailable users:')
            for u in User.objects.all()[:10]:
                self.stdout.write(f'  - {u.username}')
            return

        groweradmin_group, created = Group.objects.get_or_create(name='is_groweradmin')
        if created:
            self.stdout.write(self.style.SUCCESS('Created is_groweradmin group'))
        else:
            self.stdout.write('is_groweradmin group already exists')

        permission_codenames = []
        for perm_string in IS_GROWERADMIN:
            app_label, codename = perm_string.split('.')
            permission_codenames.append((app_label, codename))

        permissions = []
        for app_label, codename in permission_codenames:
            try:
                perm = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename
                )
                permissions.append(perm)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Permission not found: {app_label}.{codename}'))

        groweradmin_group.permissions.set(permissions)
        self.stdout.write(f'Assigned {len(permissions)} permissions to is_groweradmin group')

        if user.groups.filter(name='is_groweradmin').exists():
            self.stdout.write(self.style.WARNING(f'{username} is already in is_groweradmin group'))
        else:
            user.groups.add(groweradmin_group)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Added {username} to is_groweradmin group'))

        self.stdout.write(self.style.SUCCESS(f'\n{username} is now a grower admin'))
