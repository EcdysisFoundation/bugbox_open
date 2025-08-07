import requests


def list_upload_files():
    # local dev
    api_list_url = 'http://host.docker.internal:8090/list-upload-files/'
    # ecdysis01
    # api_list_url = 'http://10.147.19.124:8090/list-upload-files/'
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
