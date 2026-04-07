from django.contrib.auth.models import Group, Permission

from bugbox3.core import permissions


def add_group_permissions(group, the_permissions):
    """
    Add permissions to a goup from a list of preexisting permissions,
    where the perimssion is in the format of 'app_label.codename'
    """
    permissions_added = 0
    permssion_errors = []
    for v in the_permissions:
        try:
            app_label, codename = v.split('.')
            p = Permission.objects.get(
                content_type__app_label=app_label,
                codename=codename
            )
            group.permissions.add(p)
            permissions_added += 1
        except Exception:
            permssion_errors.append(v)
    return {
        'permissions_added': permissions_added,
        'permssion_errors': permssion_errors
    }


def create_app_groups():
    """
    Create the base groups expected in the app.
    """
    results = []

    # two tuple tuple of group name and list of permissions
    groups_permissions = (
        ('is_admin', permissions.IS_ADMIN),
        ('is_research', permissions.IS_RESEARCH),
        ('review_page', [permissions.REVIEW_SPECIMEN_PAGE]),
        ('is_grower', permissions.IS_GROWER),
        ('is_groweradmin', permissions.IS_GROWERADMIN),
        ('taxonomy_reviewer', permissions.TAXONOMY_REVIEWER),
        ('specimen_reviewer', permissions.SPECIMEN_REVIEWER),
    )

    for entry in groups_permissions:
        group, created = Group.objects.get_or_create(name=entry[0])
        results.append(f'{entry[0]} created {created}')
        if created:
            results.append(add_group_permissions(group, entry[1]))
        else:
            add_group_permissions(group, entry[1])

    return f'Groups created with permissions: {results}'
