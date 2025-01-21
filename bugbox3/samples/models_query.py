from organizations.models import OrganizationUser

from ..core.models import LookupChoices
from . import constants
from .models import SamplePlan


def describe_sample_plan(sample_plan):
    org_id = sample_plan.experiment.organization_id
    no_per_date = getattr(
        sample_plan, constants.FIELD_SAMPLE_PLAN_NO_PER_DATE)
    name_no_per_type = getattr(
        sample_plan, constants.FIELD_SAMPLE_PLAN_NAME_NO_PER_TYPE)
    sample_type = getattr(
        sample_plan, constants.FIELD_SAMPLE_PLAN_SAMPLE_TYPE)
    names = []
    i = no_per_date
    while i:
        names.append(name_no_per_type + str(i))
        i -= 1
    names.sort()
    names_string = ', '.join(names)
    sample_types = LookupChoices.objects.get_field_dict_w_blank(
        org_id, constants.FIELD_SAMPLE_TYPE)
    if sample_type in sample_types:
        sample_type = sample_types[sample_type]
    return {'description': '{0} {1} ({2}) per sample date'.format(
        no_per_date, sample_type, names_string),
        'no_per_date': no_per_date,
        'name_no_per_type': name_no_per_type,
        'names': names,
        'sample_type': sample_type,
        'names_string': names_string
    }


def get_sample_plan_descriptions(experiment_id):
    plans = SamplePlan.objects.filter(experiment_id=experiment_id).order_by(
        constants.FIELD_SAMPLE_PLAN_SAMPLE_TYPE)
    if plans:
        return [describe_sample_plan(p) for p in plans]
    return []


def get_user_choices(user):
    orgs = OrganizationUser.objects.filter(user=user).values_list('organization', flat=True)
    return [(u.user_id, u.user.username) for u in OrganizationUser.objects.filter(
        organization__in=orgs).order_by('user__username')]
