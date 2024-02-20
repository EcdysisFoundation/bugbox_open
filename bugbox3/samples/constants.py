# String Definitions

FIELD_UUID = 'uuid'
FIELD_NAME = 'name'
FIELD_ABBREVIATION = 'abbreviation'
FIELD_FROM_YEAR = 'from_year'
FIELD_TO_YEAR = 'to_year'
FIELD_LEADER = 'leader'
FIELD_NO_SITES = 'no_sites'
FIELD_DATE_PER_SITE = 'date_per_site'
FIELD_SAMPLE_TYPE = 'sample_type'
FIELD_NO_PER_DATE = 'no_per_date'
FIELD_NAME_NO_PER_TYPE = 'name_no_per_type'
FIELD_COMPLETED = 'completed'
FIELD_SUMMARY = 'summary'

TAXON_CLASS_ACARI = 'acari'
TAXON_CLASS_ANNELIDA = 'annelida'
TAXON_CLASS_COLLEMBOLA = 'collembola'
TAXON_CLASS_GASTROPODA = 'gastropoda'
TAXON_CLASS_NEMATODA = 'nematoda'
TAXON_CLASS_THYSANOPTERA = 'thysanoptera'

ACCEPTANCE_PENDING = 0
ACCEPTANCE_CONFIRMED = 1
ACCEPTANCE_REJECTED = 2


# Model Defaults

def sample_taxon_classes_default():
    return dict(
        TAXON_CLASS_ACARI=0,
        TAXON_CLASS_ANNELIDA=0,
        TAXON_CLASS_COLLEMBOLA=0,
        TAXON_CLASS_GASTROPODA=0,
        TAXON_CLASS_NEMATODA=0,
        TAXON_CLASS_THYSANOPTERA=0
    )


#  Model Choices

ACCEPTANCE_CHOICES = (
    (ACCEPTANCE_PENDING, 'Pending'),
    (ACCEPTANCE_CONFIRMED, 'Confirmed'),
    (ACCEPTANCE_REJECTED, 'Rejected'),
)


FORM_FIELDS_EXPERIMENT = [
    FIELD_NAME,
    FIELD_FROM_YEAR,
    FIELD_TO_YEAR,
    FIELD_LEADER,
    FIELD_COMPLETED,
    FIELD_SUMMARY,
]