# Grower Views
from .application import application_create, application_delete, application_edit, application_view
from .application_steps import (
    application_step1,
    application_step2,
    application_step3,
    application_step4,
    application_step5,
    application_step6,
)
from .profile import dashboard, grant_full_grower_permissions, profile_complete, profile_edit
from .bird_recordings import (
    bird_recording_complete,
    bird_recording_initiate,
    bird_recording_list,
    bird_recording_upload_page,
    bird_recording_validate_code,
)
from .results import basic_results_ajax, depth_options_ajax, factor_detail, results

__all__ = [
    'grant_full_grower_permissions',
    'profile_complete',
    'dashboard',
    'results',
    'bird_recording_upload_page',
    'bird_recording_list',
    'bird_recording_validate_code',
    'bird_recording_initiate',
    'bird_recording_complete',
    'basic_results_ajax',
    'depth_options_ajax',
    'factor_detail',
    'profile_edit',
    'application_create',
    'application_view',
    'application_edit',
    'application_delete',
    'application_step1',
    'application_step2',
    'application_step3',
    'application_step4',
    'application_step5',
    'application_step6',
]
