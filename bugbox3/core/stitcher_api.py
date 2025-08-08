import requests

# use for local dev
STITCHER_URL = 'http://host.docker.internal:8090'
# use for ecdysis01
# STITCHER_URL = 'http://10.147.19.124:8090'


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
    # replace these
    # local dev
    api_list_url = STITCHER_URL + '/list-upload/'
    # ecdysis01
    # api_list_url = 'http://10.147.19.124:8090/list-upload/'
    requests.get(api_list_url, params={'guid': guid})
    try:
        response = requests.get(api_list_url, params={'guid': guid})
    except Exception as e:
        print(e)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
