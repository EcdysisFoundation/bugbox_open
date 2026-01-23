from ..libs.utilities import uniform_time_display
from . import constants
from .models import TimelineEvent

# EVENT CONSTANTS
EVENT_TITLE_REVIEW = 'Reviewed'
EVENT_TITLE_UPDATE = 'Updated'
EVENT_TITLE_CREATED = 'Created'
EVENT_TITLE_UPLOADED_IMAGES = 'Uploaded images'
EVENT_BY_USERNAME = constants.FIELD_TIMELINE_EVENT_BY_USER + '__username'
EVENT_UNKNOWN_USER = 'Unknown user'

EVENT_REVIEW_COLUMNS = (
    constants.FIELD_SPECIMEN_ACCEPTANCE,
    constants.FIELD_SPECIMEN_CLASSIFICATION,
    constants.FIELD_SPECIMEN_AI_CLASSIFICATION
)
EVENT_VALUES = (
    EVENT_BY_USERNAME,
    constants.FIELD_TIMELINE_EVENT_EVENT_TITLE,
    constants.FIELD_TIMELINE_EVENT_DATE_TIME,
    constants.FIELD_TIMELINE_EVENT_BODY,
)


def get_event_body(changed, initial, instance):
    body = ''
    for c in changed:
        if body:
            body += ' '
        if c == constants.FIELD_SPECIMEN_ACCEPTANCE:
            data_values = [
                constants.ACCEPTANCE_LOOKUP[initial[c]],
                constants.ACCEPTANCE_LOOKUP[getattr(instance, c)]
            ]
        else:
            data_values = [str(initial[c]), str(getattr(instance, c))]
        body += '{0} changed from {1} to {2}.'.format(
            str(c).capitalize(), data_values[0], data_values[1]
        )
    return body


def get_event_title(changed):
    event_title = ''
    reviews = [i for i in changed if i in EVENT_REVIEW_COLUMNS]
    if reviews:
        event_title += EVENT_TITLE_REVIEW
    if len(changed) > len(reviews):
        if event_title:
            event_title += ', '
        event_title += EVENT_TITLE_UPDATE
    return event_title


def audit_specimen_update(form, user, specimen):
    changed = form.changed_data
    if form.initial[constants.FIELD_SPECIMEN_ACCEPTANCE] == getattr(
            form.instance, constants.FIELD_SPECIMEN_ACCEPTANCE):
        # changed data always includes acceptance
        changed.remove(constants.FIELD_SPECIMEN_ACCEPTANCE)
    if changed:
        TimelineEvent.objects.create(
            specimen_id=specimen.id,
            event_title=get_event_title(changed),
            by_user=user,
            body=get_event_body(changed, form.initial, form.instance)
        )


def audit_specimen_view(initial, user, specimen):
    if initial[constants.FIELD_SPECIMEN_ACCEPTANCE] != specimen.acceptance:
        # only audit review actions here
        changed = [constants.FIELD_SPECIMEN_ACCEPTANCE]
        TimelineEvent.objects.create(
            specimen_id=specimen.id,
            event_title=get_event_title(changed),
            by_user=user,
            body=get_event_body(changed, initial, specimen)
        )


def audit_upload_images(user, specimen, created_images):
    TimelineEvent.objects.create(
        specimen_id=specimen.id,
        event_title=EVENT_TITLE_UPLOADED_IMAGES,
        by_user=user,
        body='Uploaded {0} images'.format(created_images)
    )


def get_created_entry(username, date):
    return {
        EVENT_BY_USERNAME: username,
        constants.FIELD_TIMELINE_EVENT_EVENT_TITLE: EVENT_TITLE_CREATED,
        constants.FIELD_TIMELINE_EVENT_DATE_TIME: date,
        constants.FIELD_TIMELINE_EVENT_BODY: 'Submitted this observation'
    }


def timeline_events(specimen):
    user = specimen.created_by_user.username if specimen.created_by_user else EVENT_UNKNOWN_USER
    events = [get_created_entry(user, specimen.date_added)]
    events += list(TimelineEvent.objects.filter(
        specimen_id=specimen.id).values(*EVENT_VALUES))
    for e in events:
        e[constants.FIELD_TIMELINE_EVENT_DATE_TIME] = uniform_time_display(e[constants.FIELD_TIMELINE_EVENT_DATE_TIME])
    return events
