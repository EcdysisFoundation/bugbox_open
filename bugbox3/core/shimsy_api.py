import requests
from django.conf import settings


def create_rescan_request(sample_name):
    """
    Create a rescan request in Shimsy when a sample is marked as Retake in stitcher.
    Arguments:
        sample_name: The sample name in format SITE_SAMPLETYPE_TRANSECT (e.g., '1234_sw_1')
    Returns:
        dict with 'success' (bool) and 'message' (str)
    """
    shimsy_url = (settings.SHIMSY_API_URL or '').rstrip('/')
    if not shimsy_url:
        return {
            'success': False,
            'message': 'Shimsy API is not configured (set SHIMSY_API_URL).',
        }

    api_url = f'{shimsy_url}/api/rescan-request/'

    try:
        payload = {'sample_name': sample_name}
        response = requests.post(
            api_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'success': True,
                    'message': f'Rescan request created in Shimsy for {sample_name}'
                }
            else:
                return {
                    'success': False,
                    'message': f'Shimsy API returned error: {data.get("message", "Unknown error")}'
                }
        else:
            return {
                'success': False,
                'message': f'Shimsy API returned status code {response.status_code}'
            }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'message': 'Timeout connecting to Shimsy API'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'message': 'Could not connect to Shimsy API. Is Shimsy running?'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error calling Shimsy API: {str(e)}'
        }
