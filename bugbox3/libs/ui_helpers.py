
def get_numeric_dropdown(length, button_label):
    """
    Returns a numeric dropdown list of the defined length
    """
    result = '<div class="btn-group"> \
             <button type="button" class="btn btn-info dropdown-toggle" data-bs-toggle="dropdown" \
             aria-expanded="false">{}</button> \
             <ul class="dropdown-menu">'.format(button_label)
    for x in range(length):
        result += '<li><a class="dropdown-item" value="x">{}</a></li>'.format(x, x)
    result += '</ul></div>'
    return result


def get_formsets_display_control_config(formset_total, formset_intial, formset_row_prefix='formsets_row_'):
    """
    Configuration variables for static.js.jquery_tools.formsets_display_control.
    Returned as dictionary.
    """
    display_none_class = 'd-none'
    total_list_ids = []
    #initial_list_ids = []
    total_count = 1
    #initial_count = 1
    def get_formset_row(the_count):
        return '#{}{}'.format(str(formset_row_prefix), str(the_count))
        
    while total_count <= formset_total:
        formset_row = get_formset_row(total_count)
        total_list_ids.append(formset_row)
        total_count += 1
    #while initial_count <= formset_intial:
    #    formset_row = get_formset_row(initial_count)
    #    initial_list_ids.append(formset_row)
    #    initial_count += 1
    return {
        'formsets_display_control': {
            #'formset_row_prefix': formset_row_prefix,
            #'formset_total': formset_total,
            'formset_intial': formset_intial,
            'total_list_ids': total_list_ids,
            #'initial_list_ids': initial_list_ids,
            'display_none_class': display_none_class
        }
    }
