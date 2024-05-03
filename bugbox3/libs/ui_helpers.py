
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


def get_datatables_row(columns, row_styles=None, col_styles=None):
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
        for style in row_styles:
            row_style += ' {0}'.format(style)
    result = '<div class="row{0}">'.format(row_style)
    for c in columns:
        result += '<div class="col{0}">{1}</div>'.format(col_style, c)
    result += '</div></div>'
    return result
