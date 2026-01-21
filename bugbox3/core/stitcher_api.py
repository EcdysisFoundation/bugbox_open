import json
import re
import requests

STITCHER_URL = 'http://host.docker.internal:8090'

# move js_URLs dev differences to local.yml and local-cloud.yml
STITCHER_JS_URL_ZEROTIER = 'http://10.147.19.124:8090'

# for local dev
# STITCHER_JS_URL_ZEROTIER = 'http://localhost:8090'

STITCHER_JS_URL = 'http://ecdysis01.local:8090'

ERROR_MSG_KEY = 'ERROR'


def list_upload_files():
    api_list_url = STITCHER_URL + '/list-upload-files/'
    all_data = []
    offset = 0
    limit = 100

    while True:
        print('*'*100)
        params = {
            'offset': offset,
            'limit': limit,
            'approved': True
        }
        print(params)

        try:
            response = requests.get(api_list_url, params=params)
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


def get_upload_file(guid):
    api_list_url = STITCHER_URL + '/list-upload/'
    try:
        response = requests.get(api_list_url, params={'guid': guid})
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {ERROR_MSG_KEY: response.status_code}
    except Exception as e:
        print(e)
        return {ERROR_MSG_KEY: e}


def patch_upload_file(guid, data):
    api_url = STITCHER_URL + f'/update-record/{guid}'
    try:
        response = requests.patch(api_url, data=json.dumps(data))
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {ERROR_MSG_KEY: response.status_code}
    except Exception as e:
        print(e)
        return {ERROR_MSG_KEY: e}


def delete_upload_file(guid):
    api_url = STITCHER_URL + f'/delete/{guid}'
    try:
        response = requests.delete(api_url)
        if response.status_code in [200, 204]:
            return {'message': f'success code {response.status_code}'}
        else:
            return {ERROR_MSG_KEY: response.status_code}
    except Exception as e:
        print(e)
        return {ERROR_MSG_KEY: e}


def get_root_message():
    api_url = STITCHER_URL
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {ERROR_MSG_KEY: response.status_code}
    except Exception as e:
        print(e)
        return {ERROR_MSG_KEY: e}


def get_stitcher_stats():
    api_url = STITCHER_URL + '/stats/'
    try:
        response = requests.get(api_url)
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
    
    # Try to match the base pattern: SITE_TYPE_TRANSECT with optional split suffix
    # Pattern: digits_letters_Tdigits[_split_N | _splitN | _N | _a]
    match = re.match(r'^(\d+)_([a-zA-Z]+)_(T\d+)(?:_split_\d+|_split\d+|\d+|[a-z])?$', sample_name)
    
    if match:
        site = match.group(1)
        sample_type = match.group(2).lower()  # Normalize to lowercase
        transect = match.group(3)
        # Build base name without split suffix
        base_name = f"{site}_{sample_type}_{transect}"
        return (base_name, site, sample_type, transect)
    
    # Fallback: try simple split by underscore
    parts = sample_name.split('_')
    if len(parts) >= 3:
        # Remove split suffix from end if present
        if len(parts) > 3:
            # Check if last part looks like a split indicator
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


def list_retake_records():
    """
    fetches all records from Stitcher that are marked as Retake (approved=False).
    """
    api_list_url = STITCHER_URL + '/list-upload-files/'
    all_data = []
    offset = 0
    limit = 100

    while True:
        params = {
            'offset': offset,
            'limit': limit,
            'approved': False
        }

        try:
            response = requests.get(api_list_url, params=params, timeout=30)
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
    
    base_name, approved_site, approved_type, approved_transect = parsed
    
    retake_records = list_retake_records()
    
    # Filter retake records to matching records
    matching_records = []
    for record in retake_records:
        guid = record.get('guid')
        upload_dir_name = record.get('upload_dir_name')
        approved = record.get('approved')
        
        # Skip if not retake
        if approved is not False:
            continue
        
        # Skip if excluded GUID
        if exclude_guid and guid == exclude_guid:
            continue
        
        if not upload_dir_name:
            continue
        
        # Parse the retake record sample name
        record_parsed = parse_sample_name(upload_dir_name)
        if not record_parsed:
            continue
        
        _, record_site, record_type, record_transect = record_parsed
        
        # Match if has same site, type, and transect
        if (record_site == approved_site and 
            record_type == approved_type and 
            record_transect == approved_transect):
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
