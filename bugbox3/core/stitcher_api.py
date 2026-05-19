import json
import re

import requests
from django.conf import settings
from requests.exceptions import Timeout

ERROR_MSG_KEY = 'ERROR'
_STITCHER_NOT_CONFIGURED = 'STITCHER_API_URL is not configured'


def get_stitcher_api_url():
    return (settings.STITCHER_API_URL or '').rstrip('/')


def get_stitcher_js_url(*, zerotier=False):
    if zerotier:
        url = settings.STITCHER_JS_URL_ZEROTIER or settings.STITCHER_JS_URL
    else:
        url = settings.STITCHER_JS_URL
    return (url or '').rstrip('/')


def get_stitcher_flower_url():
    return (settings.STITCHER_FLOWER_URL or '').rstrip('/')


def _stitcher_not_configured():
    return {ERROR_MSG_KEY: _STITCHER_NOT_CONFIGURED}


def list_upload_files():
    base = get_stitcher_api_url()
    if not base:
        return []

    api_list_url = base + '/list-upload-files/'
    all_data = []
    offset = 0
    limit = 100

    while True:
        print('*' * 100)
        params = {
            'offset': offset,
            'limit': limit,
            'approved': True
        }
        print(params)

        try:
            response = requests.get(api_list_url, params=params, timeout=25)
        except Exception as e:
            print(e)
            break

        if response.status_code == 200:
            data = response.json()
            if not data:
                break

            all_data.extend(data)
            offset += limit
        else:
            print(f"Error: {response.status_code}")
            break

    return all_data


def simple_response_wguid(guid, api_url):
    try:
        response = requests.get(api_url, params={'guid': guid}, timeout=25)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {ERROR_MSG_KEY: response.status_code}
    except Timeout as e:
        print(e)
        e_message = f'Request timeout, the application is busy, please check back {e}'
        return {ERROR_MSG_KEY: e_message}
    except Exception as e:
        print(e)
        return {ERROR_MSG_KEY: e}


def get_upload_file(guid):
    base = get_stitcher_api_url()
    if not base:
        return _stitcher_not_configured()
    api_list_url = base + '/list-upload-w-task/'
    return simple_response_wguid(guid, api_list_url)


def get_list_upload_abridged(guid):
    base = get_stitcher_api_url()
    if not base:
        return _stitcher_not_configured()
    api_list_url = base + '/list-upload-abridged/'
    return simple_response_wguid(guid, api_list_url)


def get_only_upload_file(guid):
    base = get_stitcher_api_url()
    if not base:
        return _stitcher_not_configured()
    api_list_url = base + '/list-upload/'
    return simple_response_wguid(guid, api_list_url)


def patch_upload_file(guid, data):
    base = get_stitcher_api_url()
    if not base:
        return _stitcher_not_configured()
    api_url = base + f'/update-record/{guid}'
    try:
        response = requests.patch(api_url, data=json.dumps(data), timeout=25)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {ERROR_MSG_KEY: response.status_code}
    except Timeout as e:
        print(e)
        e_message = f'Request timeout, the application is busy, please check back {e}'
        return {ERROR_MSG_KEY: e_message}
    except Exception as e:
        print(e)
        return {ERROR_MSG_KEY: e}


def delete_upload_file(guid):
    base = get_stitcher_api_url()
    if not base:
        return _stitcher_not_configured()
    api_url = base + f'/delete/{guid}'
    try:
        response = requests.delete(api_url, timeout=25)
        if response.status_code in [200, 204]:
            return {'message': f'success code {response.status_code}'}
        else:
            return {ERROR_MSG_KEY: response.status_code}
    except Exception as e:
        print(e)
        return {ERROR_MSG_KEY: e}


def get_root_message():
    base = get_stitcher_api_url()
    if not base:
        return _stitcher_not_configured()
    try:
        response = requests.get(base, timeout=25)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {ERROR_MSG_KEY: response.status_code}
    except Exception as e:
        print(e)
        return {ERROR_MSG_KEY: e}


def get_stitcher_stats():
    base = get_stitcher_api_url()
    if not base:
        return _stitcher_not_configured()
    api_url = base + '/stats/'
    try:
        response = requests.get(api_url, timeout=25)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {ERROR_MSG_KEY: response.status_code}
    except Exception as e:
        print(e)
        return {ERROR_MSG_KEY: e}


def parse_sample_name(sample_name):
    """
    extracts (site, sample type, transect) and removes split suffix
    """
    if not sample_name:
        return None

    match = re.match(r'^(\d+)_([a-zA-Z]+)_(T\d+)(?:_split_\d+|_split\d+|\d+|[a-z])?$', sample_name)

    if match:
        site = match.group(1)
        sample_type = match.group(2).lower()
        transect = match.group(3)
        base_name = f"{site}_{sample_type}_{transect}"
        return (base_name, site, sample_type, transect)

    parts = sample_name.split('_')
    if len(parts) >= 3:
        if len(parts) > 3:
            last_part = parts[-1]
            if re.match(r'^(split\s*\d+|\d+|[a-z])$', last_part, re.IGNORECASE):
                parts = parts[:-1]
                base_name = '_'.join(parts)
            else:
                base_name = '_'.join(parts[:-1])
        else:
            base_name = '_'.join(parts)

        site = parts[0]
        sample_type = parts[1].lower()
        transect = parts[2] if len(parts) > 2 else None

        if site and sample_type and transect:
            return (base_name, site, sample_type, transect)

    return None


def list_retake_records(upload_dir_name=None):
    """
    fetches records from Stitcher that are marked as Retake (approved=False).
    """
    base = get_stitcher_api_url()
    if not base:
        return []

    api_list_url = base + '/list-upload-files/'
    all_data = []
    offset = 0
    limit = 100

    while True:
        params = {
            'offset': offset,
            'limit': limit,
            'approved': False
        }

        if upload_dir_name:
            params['upload_dir_name'] = upload_dir_name

        try:
            response = requests.get(api_list_url, params=params, timeout=25)
        except Exception as e:
            print(f"Error fetching retake records: {e}")
            break

        if response.status_code == 200:
            data = response.json()
            if not data:
                break

            all_data.extend(data)
            offset += limit
        else:
            print(f"Error fetching retake records: {response.status_code}")
            break

    return all_data


def find_matching_retake_records(approved_sample_name, exclude_guid=None):
    """
    Find all retake records in Stitcher that match the approved sample (exclude_guid is the approved record itself).
    """
    # Parse the approved sample to get base components
    parsed = parse_sample_name(approved_sample_name)
    if not parsed:
        return []

    base_name, _, _, _ = parsed

    retake_records = list_retake_records(upload_dir_name=base_name)

    # Filter out the approved record itself
    matching_records = []
    for record in retake_records:
        guid = record.get('guid')
        upload_dir_name = record.get('upload_dir_name')

        # Skip the (approved record itself = excluded GUID)
        if exclude_guid and guid == exclude_guid:
            continue

        if not upload_dir_name:
            continue

        matching_records.append({
            'guid': guid,
            'upload_dir_name': upload_dir_name
        })

    return matching_records


def cleanup_matching_retake_records(approved_sample_name, approved_guid):
    """
    Find and delete all matching retake records from Stitcher when a sample is approved.
    """
    matching_records = find_matching_retake_records(approved_sample_name, exclude_guid=approved_guid)

    if not matching_records:
        return {
            'deleted_count': 0,
            'errors': [],
            'deleted_samples': []
        }

    deleted_count = 0
    errors = []
    deleted_samples = []

    for record in matching_records:
        guid = record['guid']
        upload_dir_name = record['upload_dir_name']

        try:
            result = delete_upload_file(guid)
            if ERROR_MSG_KEY in result:
                errors.append({
                    'sample': upload_dir_name,
                    'guid': guid,
                    'error': result[ERROR_MSG_KEY]
                })
            else:
                deleted_count += 1
                deleted_samples.append(upload_dir_name)
        except Exception as e:
            errors.append({
                'sample': upload_dir_name,
                'guid': guid,
                'error': str(e)
            })

    return {
        'deleted_count': deleted_count,
        'errors': errors,
        'deleted_samples': deleted_samples
    }
