from django.core.management.base import BaseCommand
from organizations.models import Organization
from organizations.utils import create_organization

from bugbox3.core.permissions_utils import create_app_groups
from bugbox3.core.utils import create_default_lookup_choices
from bugbox3.users.models import User


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to provide organization access')

    def handle(self, *args, **options):
        username = options.get('username')
        org_name = 'Primary_org'

        v = create_app_groups()
        print(v)

        if username:
            user = User.objects.get(username=username)
            if not Organization.objects.filter(name=org_name).exists():
                v = create_organization(user, org_name, org_user_defaults={'is_admin': True})
                print(f'Created organization {org_name} the owner is {v.owner.organization_user.user}')
            else:
                print(f'The organization with name {org_name} already exists.')
            org = Organization.objects.get(name=org_name)
            org.add_user(user, is_admin=True)

        if Organization.objects.filter(name=org_name).exists():
            primary_org = Organization.objects.get(name=org_name)
            v = create_default_lookup_choices(primary_org.id)
            print(v)
