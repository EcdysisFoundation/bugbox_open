from bugbox3.core.constants import (
    DEFAULT_SITE_HABITAT_TYPE_CHOICES,
    DEFAULT_SITE_TREATMENT_CHOICES,
    DEFAULT_TAG_CHOICES,
)
from bugbox3.core.models import LookupChoices
from bugbox3.samples.constants import (
    FIELD_SAMPLE_TYPE,
    FIELD_SITE_HABITAT_TYPE,
    FIELD_SITE_TREATMENT,
    FIELD_SPECIMEN_TAGS,
    SAMPLE_TYPE_CHOICES,
)


def create_default_lookup_choices(org_id):
    """
    Given an organization ID, enter a default set of choices, if they dont already have some.
    """
    recs = LookupChoices.objects.filter(organization_id=org_id)
    if recs:
        warning_message = f'Org id {org_id} already has {len(recs)} entries in choices. ' \
            'Delete those to be able to use this command'
        return warning_message

    # the field_options given as (field, ((entry, display_txt),)
    field_options = (
        (FIELD_SPECIMEN_TAGS, DEFAULT_TAG_CHOICES),
        (FIELD_SITE_TREATMENT, DEFAULT_SITE_TREATMENT_CHOICES),
        (FIELD_SITE_HABITAT_TYPE, DEFAULT_SITE_HABITAT_TYPE_CHOICES),
        (FIELD_SAMPLE_TYPE, SAMPLE_TYPE_CHOICES)
    )
    created_objects = 0
    for entry in field_options:
        field_entry = entry[0]
        for v in entry[1]:
            LookupChoices.objects.create(
                organization_id=org_id,
                field=field_entry,
                entry=v[0],
                display_txt=v[1]
            )
            created_objects += 1
    return f'Created {created_objects} LookupChoices entries.'
