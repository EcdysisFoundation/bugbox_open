import $ from 'jquery';
import { Modal } from 'bootstrap';

// Misc., reusable jquery UI tools.
// requires a json_context
// requires messageModal be present in template, see base.html

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    var messageModalBody = document.getElementById('messageModal-body');
    var messageModal = new Modal(document.getElementById('messageModal'), {
        keyboard: false
      })
    

    if ('formsets_display_control' in json_context) {
        // use libs.ui_helpers.get_formsets_display_control_config to set correct configuration
        // expects formsets in the view where form layout injects <div id='formsets_row_{{ forloop.counter }}'>
        // wrapper around the formset, initialy set as bootrap css 'd-none', reveal the initial rows with ability
        // to show additional formsets on the page, up to the total available.

        // get the tool configuration
        let tool_config = json_context.formsets_display_control
        let max_rows = tool_config.total_list_ids.length
        // uses messageModal in base template
        // display the inital rows
        let i = 0;
        while (i < tool_config.formset_intial) {
            i++;
            let row = tool_config.total_list_ids.shift();
            $(row).removeClass(tool_config.display_none_class);
        }

        // button to show more rows
        let $displayFormsetRowButton = $('<button type="button" id="displayFormsetRow" class="btn btn-link btn-small">Add Sample Type </button>')
        $('.display-formset-row-button').append($displayFormsetRowButton)
        $displayFormsetRowButton.on('click', function() {
            if (tool_config.total_list_ids.length > 0) {
                let row = tool_config.total_list_ids.shift();
                $(row).removeClass(tool_config.display_none_class);
            } else {
                messageModalBody.innerHTML = `<p>Maximum addable rows (${max_rows}) reached.</p>`;
                messageModal.show();
            };
        })

    }
        
});
