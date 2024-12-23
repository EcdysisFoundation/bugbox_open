import logging

import requests
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from requests import RequestException

from config import celery_app


def image_prediction(image_bytes):
    if not settings.AI_INFERENCE_URL:
        return
    files = {'file': image_bytes}
    response = requests.post(settings.AI_INFERENCE_URL, files=files)
    try:
        response.raise_for_status()
        response = response.json()
        return response
    except Exception as e:
        print('image_prediction didnt get a 200 response, try again later... ' + e)
    return None


@celery_app.task(autoretry_for=(RequestException,), soft_time_limit=240,
                 retry_kwargs={'max_retries': 3, 'countdown': 30},
                 retry_backoff=True)
def id_image(id):
    """Task to run ml model to id the image"""
    Specimen = apps.get_model(app_label='samples', model_name='Specimen')
    try:
        specimen = Specimen.objects.get(id=id)
    except Specimen.DoesNotExist:
        print('DoesNotExist: specimen id {0}'.format(id))
        return
    # dont re classify reviewed specimens
    if specimen.acceptance != 0:
        print(str(id) + ' is not acceptance = 0, returning...')
        return
    image_set_filtered = specimen.specimenimage_set.exclude(
        image_notfound=True
    )
    specimenimage = image_set_filtered.first()
    if not specimenimage:
        print(str(id) + ' has no SpecimenImage, returning...')
        return
    try:
        data = image_prediction(specimenimage.image)
    except SoftTimeLimitExceeded:
        logging.exception('SoftTimeLimitExceeded on id_image of specimen id: {}'.format(id))
        data = None
    except FileNotFoundError as e:
        print(e)
        data = None
        print('setting image_notfound to True')
        specimenimage.image_notfound = True
        specimenimage.save()

    # dont make changes if we didnt get data
    if not data:
        return
    Morphospecies = apps.get_model(app_label='taxonomy', model_name='Morphospecies')
    morphospecies_id = data.get("morphospecies_id")
    specimen.ai_classification = Morphospecies.objects.get(pk=int(morphospecies_id))
    specimen.ai_model_name = data.get("modelVersion")
    specimen.confidence = float(data.get("confidence"))
    specimen.optional_pred_one = data.get("optional_preds")[0]
    specimen.optional_pred_two = data.get("optional_preds")[1]
    specimen.save()
    return


# only run on Ecdysis01
@shared_task
def run_classify_new_images():
    call_command('classify_new_images')


# only run on Ecdysis01
@shared_task
def run_update_classifications():
    call_command('update_classifications')


# only run on Ecdysis01
# will need replaced to be specific to Ecdysis data when more orgs exist
@shared_task
def run_s3_media_download():
    call_command('bash_script s3_media_download.sh')
