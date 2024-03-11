from . import constants
from .models import SamplePlan


def describe_sample_plan(sample_plan):
    no_per_date = getattr(sample_plan, constants.FIELD_SAMPLE_PLAN_NO_PER_DATE)
    name_no_per_type = getattr(sample_plan, constants.FIELD_SAMPLE_PLAN_NAME_NO_PER_TYPE)
    names = []
    i = no_per_date
    while i:
        names.append(name_no_per_type + str(i))
        i -= 1
    names.sort()
    print(no_per_date)
    print()
    print()
    return '{0} {1} ({2}) per sample date per site'.format(
        no_per_date,
        constants.SAMPLE_TYPE_CHOICES_DICT[getattr(sample_plan, constants.FIELD_SAMPLE_PLAN_SAMPLE_TYPE)],
        ', '.join(names))


def get_sample_plan_descriptions(experiment_id):
    plans = SamplePlan.objects.filter(experiment_id=experiment_id).order_by(
        constants.FIELD_SAMPLE_PLAN_SAMPLE_TYPE)
    if plans:
        return [describe_sample_plan(p) for p in plans]
    return []
