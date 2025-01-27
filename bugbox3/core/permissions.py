ADD_MORPHOSPECIES = 'taxonomy.add_morphospecies'
CHANGE_MORPHOSPECIES = 'taxonomy.change_morphospecies'
DELETE_MORPHOSPECIES = 'taxonomy.delete_morphospecies'
VIEW_MORPHOSPECIES = 'taxonomy.view_morphospecies'

ADD_AITRAINING = 'taxonomy.add_aitraining'
CHANGE_AITRAINING = 'taxonomy.change_aitraining'
DELETE_AITRAINING = 'taxonomy.delete_aitraining'
VIEW_AITRAINING = 'taxonomy.view_aitraining'

ADD_SPECIMEN = 'samples.add_specimen'
CHANGE_SPECIMEN = 'samples.change_specimen'
DELETE_SPECIMEN = 'samples.delete_specimen'
VIEW_SPECIMEN = 'samples.view_specimen'
ADD_SAMPLE = 'samples.add_sample'
CHANGE_SAMPLE = 'samples.change_sample'
DELETE_SAMPLE = 'samples.delete_sample'
VIEW_SAMPLE = 'samples.view_sample'
ADD_SPECIMENIMAGE = 'samples.add_specimenimage'
CHANGE_SPECIMENIMAGE = 'samples.change_specimenimage'
DELETE_SPECIMENIMAGE = 'samples.delete_specimenimage'
VIEW_SPECIMENIMAGE = 'samples.view_specimenimage'
ADD_SAMPLEPLAN = 'samples.add_sampleplan'
CHANGE_SAMPLEPLAN = 'samples.change_sampleplan'
DELETE_SAMPLEPLAN = 'samples.delete_sampleplan'
VIEW_SAMPLEPLAN = 'samples.view_sampleplan'
ADD_EXPERIMENT = 'samples.add_experiment'
CHANGE_EXPERIMENT = 'samples.change_experiment'
DELETE_EXPERIMENT = 'samples.delete_experiment'
VIEW_EXPERIMENT = 'samples.view_experiment'
ADD_TIMELINEEVENT = 'samples.add_timelineevent'
CHANGE_TIMELINEEVENT = 'samples.change_timelineevent'
DELETE_TIMELINEEVENT = 'samples.delete_timelineevent'
VIEW_TIMELINEEVENT = 'samples.view_timelineevent'
ADD_SITE = 'samples.add_site'
CHANGE_SITE = 'samples.change_site'
DELETE_SITE = 'samples.delete_site'
VIEW_SITE = 'samples.view_site'
ADD_SITEVISIT = 'samples.add_sitevisit'
CHANGE_SITEVISIT = 'samples.change_sitevisit'
DELETE_SITEVISIT = 'samples.delete_sitevisit'
VIEW_SITEVISIT = 'samples.view_sitevisit'

ADD_LOOKUPCHOICES = 'core.add_lookupchoices'
CHANGE_LOOKUPCHOICES = 'core.change_lookupchoices'
DELETE_LOOKUPCHOICES = 'core.delete_lookupchoices'

REVIEW_SPECIMEN_PAGE = 'samples.review_specimen_page'

IS_RESEARCH = [
    VIEW_MORPHOSPECIES,
    ADD_SPECIMEN,
    CHANGE_SPECIMEN,
    DELETE_SPECIMEN,
    VIEW_SPECIMEN,
    ADD_SAMPLE,
    CHANGE_SAMPLE,
    DELETE_SAMPLE,
    VIEW_SAMPLE,
    ADD_SPECIMENIMAGE,
    CHANGE_SPECIMENIMAGE,
    DELETE_SPECIMENIMAGE,
    VIEW_SPECIMENIMAGE,
    ADD_SAMPLEPLAN,
    CHANGE_SAMPLEPLAN,
    DELETE_SAMPLEPLAN,
    VIEW_SAMPLEPLAN,
    ADD_EXPERIMENT,
    CHANGE_EXPERIMENT,
    VIEW_EXPERIMENT,
    ADD_TIMELINEEVENT,
    CHANGE_TIMELINEEVENT,
    DELETE_TIMELINEEVENT,
    VIEW_TIMELINEEVENT,
    ADD_SITE,
    CHANGE_SITE,
    DELETE_SITE,
    VIEW_SITE,
    ADD_SITEVISIT,
    CHANGE_SITEVISIT,
    DELETE_SITEVISIT,
    VIEW_SITEVISIT,
]

IS_ADMIN = [
    ADD_LOOKUPCHOICES,
    CHANGE_LOOKUPCHOICES,
    DELETE_LOOKUPCHOICES,
]


def show_toolbar(request):
    return str(request.user) == 'mikaylaelectra'
