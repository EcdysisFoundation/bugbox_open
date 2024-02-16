
# String Definitions

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
