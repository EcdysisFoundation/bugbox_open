from django.conf import settings
from django.core.files.storage import default_storage
from django.urls import reverse

from bugbox3.samples import constants
from bugbox3.taxonomy import constants as constants_tax

from .utilities import get_media_url

"""
UI Helpers. Many of these may be better moved to .js webpack modules.
"""

DISABLED_DELETE_CHECK = '''<div class="form-check">
  <input class="form-check-input" type="checkbox" value="" id="flexCheckIndeterminateDisabled" disabled>
  <label class="form-check-label" for="flexCheckIndeterminateDisabled">
    Delete
  </label>
</div>'''


def get_numeric_dropdown(length, button_label):
    """
    Returns a numeric dropdown list of the defined length
    """
    result = '<div class="btn-group"> \
             <button type="button" class="btn btn-info dropdown-toggle" data-bs-toggle="dropdown" \
             aria-expanded="false">{}</button> \
             <ul class="dropdown-menu">'.format(button_label)
    for x in range(length):
        result += '<li><a class="dropdown-item" value="x">{}</a></li>'.format(x)
    result += '</ul></div>'
    return result


def get_formsets_display_control_config(formset_total, formset_intial, formset_row_prefix='formsets_row_'):
    """
    Configuration variables for static.js.jquery_tools.formsets_display_control.
    Returned as dictionary.
    """
    display_none_class = 'd-none'
    total_list_ids = []
    total_count = 1

    def get_formset_row(the_count):
        return '#{}{}'.format(str(formset_row_prefix), str(the_count))

    while total_count <= formset_total:
        formset_row = get_formset_row(total_count)
        total_list_ids.append(formset_row)
        total_count += 1

    return {
        'formsets_display_control': {
            'formset_intial': formset_intial,
            'total_list_ids': total_list_ids,
            'display_none_class': display_none_class
        }
    }


def get_datatables_container(rows, container_styles=None):
    """
    Put rows in a container for display in a datatables row.
    rows are formated grid row, col html.
    container_style are an optional iterable with styles to apply.
    """
    styles = ''
    if container_styles:
        for style in container_styles:
            styles += ' {0}'.format(style)
    return '<div class="container text-center{0}">{1}</div>'.format(styles, rows)


def get_datatables_row(columns, row_styles=(), col_styles=()):
    """
    Return a stylized row for datatables cell as row with columns
    columns and styles are iterables.
    """
    row_style = ''
    col_style = ''
    if row_styles:
        for style in row_styles:
            row_style += ' {0}'.format(style)
    if col_styles:
        for style in col_styles:
            col_style += ' {0}'.format(style)
    result = '<div class="row{0}">'.format(row_style)
    for c in columns:
        result += '<div class="col{0}">{1}</div>'.format(col_style, c)
    result += '</div></div>'
    return result


def get_img_src(img_field, resize_width=None, styles='', public=False):
    """
    Get an html img tag formated from an ImageField.
    Styes should be a string of styes, exampe 'c-1 c-2'
    """
    if img_field and not default_storage.exists(img_field.name):
        return '<i class="bi bi-question-diamond"></i>'

    def img_src(path, width, height, styles):
        return '<img src="{0}" width="{1}" height="{2}" class="{3}">'.format(
            path,
            width,
            height,
            str(styles)
        )

    if img_field and not resize_width:
        return img_src(
            get_media_url(img_field, public),
            img_field.width,
            img_field.height,
            str(styles)
        )
    elif img_field and resize_width:
        return img_src(
            get_media_url(img_field, public),
            int(resize_width),
            int(resize_width) * (img_field.height / img_field.width),
            str(styles)
        )
    else:
        return '<i class="bi bi-bug"></i>'


def get_img_captioned(img_field, caption, resize_width=None, public=False):
    """
    Get the image src with a caption.
    Styes should be a string of styes, exampe 'c-1 c-2'
    """
    src = get_img_src(
        img_field,
        resize_width=resize_width,
        styles='figure-img img-fluid rounded',
        public=public)
    return """
            <figure class="figure">
            {0}
            <figcaption class="figure-caption text-end fst-italic">{1}</figcaption>
            </figure>
           """.format(src, caption)


def calc_image_height(size, height, width):
    return size * (height / width)


def classify_specimen_button(specimen, img_exists):
    if not img_exists or not settings.AI_INFERENCE_URL:
        return ''
    disabled = ' disabled' if specimen.acceptance > 0 else ''
    href = 'href="{0}" '.format(
        reverse('taxonomy:classify-specimen', kwargs={'id': specimen.id})) if not disabled else ''
    aria_disabled = ' aria-disabled="true"' if disabled else ''

    return '<a {0}role="button"{1}'.format(href, aria_disabled) + \
           'class="btn btn-sm btn-outline-danger{0}">Classify</a>'.format(disabled)


def get_canonical_name(moprhospecies):
    if moprhospecies.gbif_rank == constants_tax.GBIF_RANK_SPECIES:
        return '<i>{0}</i>'.format(moprhospecies.gbif_canonical_name)
    return moprhospecies.gbif_canonical_name


def get_classifcation(specimen):
    if specimen.acceptance and specimen.classification:
        return '{0}<br/>{1}'.format(
            specimen.classification.name, get_canonical_name(specimen.classification))
    elif specimen.classification and not specimen.ai_classification:
        return '{0}<br/>{1}'.format(
            specimen.classification.name, get_canonical_name(specimen.classification))
    elif specimen.acceptance != constants.ACCEPTANCE_REJECTED and specimen.ai_classification:
        return '{0}<br/>{1}'.format(
            specimen.ai_classification.name, get_canonical_name(specimen.ai_classification))
    elif specimen.specimenimage_set.first() and specimen.acceptance == constants.ACCEPTANCE_PENDING:
        return constants.ACCEPTANCE_LOOKUP[specimen.acceptance]
    elif specimen.specimenimage_set.first() and specimen.acceptance == constants.ACCEPTANCE_REJECTED:
        return constants.ACCEPTANCE_LOOKUP[specimen.acceptance]
    else:
        return ''


def get_probability(specimen):
    if specimen.confidence and specimen.ai_model_name:
        bg_class = 'bg-danger'
        if specimen.confidence >= 60:
            bg_class = 'bg-success'
        elif specimen.confidence >= 30:
            bg_class = 'bg-warning'
        return """<div class="progress">
                    <div class="progress-bar {0}" role="progressbar"
                    aria-label="Success example" style="width: {1}%"
                    aria-valuenow="{1}" aria-valuemin="0" aria-valuemax="100">{1}%</div>
                    </div>""".format(bg_class, specimen.confidence)
    elif specimen.specimenimage_set.first():
        return 'Pending'
    else:
        return ''


def get_version(specimen):
    if specimen.ai_model_name:
        return 'MorphoMF v' + specimen.ai_model_name
    return ''


def get_probability_or_user(specimen):
    if specimen.acceptance == constants.ACCEPTANCE_REJECTED or (
            specimen.classification and not specimen.ai_classification):
        return '<span class="badge text-bg-success">{0}</span>'.format(specimen.reviewer_user)
    else:
        return '{0}{1}'.format(get_probability(specimen), get_version(specimen))


def get_ai_classification(specimen):
    if not specimen.ai_classification:
        return ''
    return '<p>{0}<br/>{1}{2}{3}</p>'.format(
        specimen.ai_classification.name,
        get_canonical_name(specimen.ai_classification),
        get_probability(specimen),
        get_version(specimen))


def get_sample_discription(sample):
    lim = 35
    x = '{0}, {1}, {2}'.format(
        sample.name_no,
        sample.site_visit.site.site_name,
        sample.sample_type)
    if len(x) > lim:
        x = x[:lim] + '...'
    return x


def get_specimen_context(specimen):
    """
    Get a description with links of the specimen context for display as html.
    """
    e = '<a href="{0}" target="_blank">{1}</a>'.format(
        reverse('samples:experiment', kwargs={
                'experiment_id': specimen.sample.site_visit.site.experiment.id}),
        specimen.sample.site_visit.site.experiment.name
    )
    s = '<a href="{0}" target="_blank">{1}</a>'.format(
         reverse('samples:sample', kwargs={
                 'sample_id': specimen.sample.id}),
         get_sample_discription(specimen.sample)
    )
    return '{0}<br/>{1}<br/>{2}'.format(
        e, specimen.sample.site_visit.visit_date.strftime("%d-%b-%Y"), s
    )


def get_specimen_location(specimen):
    """
    Get the location description from a specimen record.
    """
    return ', '.join(
        (specimen.sample.site_visit.site.country,
         specimen.sample.site_visit.site.state_region,
         specimen.sample.site_visit.site.county_region)
    )
