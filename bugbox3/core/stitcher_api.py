import json
import requests

STITCHER_URL = 'http://host.docker.internal:8090'

STITCHER_JS_URL_ZEROTIER = 'http://10.147.19.124:8090'
# or
STITCHER_JS_URL = 'http://ecdysis01.local:8090'


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
            'label_studio_filter': True
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
            return {'message': response.status_code}
    except Exception as e:
        return {'message': e}


def patch_upload_file(guid, data):
    api_url = STITCHER_URL + f'/update-record/{guid}'
    try:
        response = requests.patch(api_url, data=json.dumps(data))
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {'message': response.status_code}
    except Exception as e:
        return {'message': e}
