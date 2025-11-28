"""
Management command to assign grower admin permissions to users in the is_groweradmin group
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from bugbox3.core.permissions import IS_GROWERADMIN

User = get_user_model()


class Command(BaseCommand):
    help = 'Assign grower admin permissions to users in the is_groweradmin group'

    def handle(self, *args, **options):
        self.stdout.write('Assigning grower admin permissions...')
        
        # Get or create is_groweradmin group
        groweradmin_group, created = Group.objects.get_or_create(name='is_groweradmin')
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created is_groweradmin group'))
        else:
            self.stdout.write(f'is_groweradmin group already exists')
        
        # Get all permissions for IS_GROWERADMIN
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
                self.stdout.write(f'  Found permission: {app_label}.{codename}')
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  Permission not found: {app_label}.{codename}'))
        
        # Assign permissions to group
        groweradmin_group.permissions.set(permissions)
        self.stdout.write(self.style.SUCCESS(f'Assigned {len(permissions)} permissions to is_groweradmin group'))
        
        # Show users in group
        groweradmin_users = User.objects.filter(groups=groweradmin_group)
        self.stdout.write(f'\nUsers in is_groweradmin group: {groweradmin_users.count()}')
        for user in groweradmin_users:
            self.stdout.write(f'  - {user.username} ({user.email})')
        
        self.stdout.write(self.style.SUCCESS('\nDone!'))


