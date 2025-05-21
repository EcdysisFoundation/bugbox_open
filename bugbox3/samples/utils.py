from django.contrib.auth import get_user_model
from django.db.models import Count
from bugbox3.samples.models import SpecimenImage, MultiSpecimenImage

User = get_user_model()

def get_user_display(user_id):
    try:
        u = User.objects.get(id=user_id)
        if u.name and u.name.strip():
            parts = u.name.strip().split()
            first = parts[0]
            last_initial = f" {parts[1][0].upper()}" if len(parts) > 1 and parts[1] else ''
            return f"{first}{last_initial}"
        elif u.username:
            return u.username
        elif u.email:
            return u.email
        else:
            return "Unknown"
    except User.DoesNotExist:
        return "Unknown"


def resolve_entered_by(sample):
    specimen_uploader = (
        SpecimenImage.objects
        .filter(specimen__sample=sample, uploaded_by_user__isnull=False)
        .values('uploaded_by_user')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )

    multi_uploader = (
        MultiSpecimenImage.objects
        .filter(sample=sample, uploaded_by_user__isnull=False)
        .values('uploaded_by_user')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )

    if specimen_uploader and multi_uploader:
        if specimen_uploader['count'] >= multi_uploader['count']:
            return get_user_display(specimen_uploader['uploaded_by_user'])
        else:
            return get_user_display(multi_uploader['uploaded_by_user'])
    elif specimen_uploader:
        return get_user_display(specimen_uploader['uploaded_by_user'])
    elif multi_uploader:
        return get_user_display(multi_uploader['uploaded_by_user'])
    elif sample.created_by_user:
        return get_user_display(sample.created_by_user.id)
    elif getattr(sample.site_visit.site, 'created_by', None):
        return get_user_display(sample.site_visit.site.created_by.id)
    else:
        return "Unknown"
