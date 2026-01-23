"""
Management command to assign grower permissions to users in the is_grower group
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from bugbox3.core.permissions import IS_GROWER_USER

User = get_user_model()


class Command(BaseCommand):
    help = 'Assign grower permissions to users in the is_grower group'

    def handle(self, *args, **options):
        self.stdout.write('Assigning grower permissions...')

        # Get or create is_grower group
        grower_group, created = Group.objects.get_or_create(name='is_grower')
        if created:
            self.stdout.write(self.style.SUCCESS('Created is_grower group'))
        else:
            self.stdout.write('is_grower group already exists')

        permission_codenames = []
        for perm_string in IS_GROWER_USER:
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
                self.stdout.write(f'  Found permission: {app_label}.{codename}')
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  Permission not found: {app_label}.{codename}'))

        # Assign permissions to group
        grower_group.permissions.set(permissions)
        self.stdout.write(self.style.SUCCESS(f'Assigned {len(permissions)} permissions to is_grower group'))

        # Show users in group
        grower_users = User.objects.filter(groups=grower_group)
        self.stdout.write(f'\nUsers in is_grower group: {grower_users.count()}')
        for user in grower_users:
            self.stdout.write(f'  - {user.username} ({user.email})')

        self.stdout.write(self.style.SUCCESS('\nDone!'))
