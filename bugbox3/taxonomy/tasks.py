import logging

import requests
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.apps import apps
from django.conf import settings
from django.core.management import call_command

from config import celery_app


def image_prediction(image_bytes):
    if not settings.AI_INFERENCE_URL:
        logging.warning("AI_INFERENCE_URL not set.")
        return None

    files = {'file': image_bytes}
    try:
        response = requests.post(
            settings.AI_INFERENCE_URL + 'metaformer-predict',
            files=files,
            timeout=10  #timeout to avoid hanging requests
        )
        response.raise_for_status()
        response = response.json()
        return response[0] if response else None  #check for empty response
    except requests.exceptions.ConnectionError as e:
        logging.error(f"[AI_INFERENCE] Connection refused: {e}")  # Log if inference server is unreachable (connection refused)
    except requests.exceptions.Timeout as e:
        logging.error(f"[AI_INFERENCE] Request timed out: {e}")  #Timeout logging
    except requests.exceptions.RequestException as e:
        logging.error(f"[AI_INFERENCE] General request failure: {e}")
    except Exception as e:
        logging.exception(f"[AI_INFERENCE] Unexpected error occurred during image prediction {e}")  # Catch-all errors
    return None


@celery_app.task(soft_time_limit=240)
def id_image(id):
    """Task to run ml model to id the image"""
    Specimen = apps.get_model(app_label='samples', model_name='Specimen')
    try:
        specimen = Specimen.objects.get(id=id)
    except Specimen.DoesNotExist:
        logging.warning(f"Specimen with id={id} does not exist.")
        return
    # dont re classify reviewed specimens
    if specimen.acceptance != 0:
        logging.info(f"Specimen with id={id} is not acceptance = 0, returning...")
        return

    image_set_filtered = specimen.specimenimage_set.exclude(image_notfound=True)
    specimenimage = image_set_filtered.first()
    if not specimenimage:
        logging.info(f"Specimen with id={id} has no SpecimenImage, returning...")
        return

    try:
        data = image_prediction(specimenimage.image)
    except SoftTimeLimitExceeded:
        logging.exception('SoftTimeLimitExceeded on id_image of specimen id: {}'.format(id))
        data = None
    except FileNotFoundError as e:
        logging.warning(f"FileNotFoundError for specimen id={id}: {e}")
        data = None
        logging.info(f"Setting image_notfound=True for specimen image in specimen id={id}")
        specimenimage.image_notfound = True
        specimenimage.save()

    # dont make changes if we didnt get data (dont update DB if no detection result was returned)
    if not data:
        logging.info(f"No AI classification returned for specimen id: {id}")  #log missing prediction
        return

    Morphospecies = apps.get_model(app_label='taxonomy', model_name='Morphospecies')
    morphospecies_id = data.get("morphospecies_id")
    if morphospecies_id:
        specimen.ai_classification = Morphospecies.objects.get(pk=int(morphospecies_id))
        specimen.ai_model_name = data.get("modelVersion")
        specimen.confidence = float(data.get("confidence"))
        specimen.optional_pred_one = data.get("optional_preds")[0]
        specimen.optional_pred_two = data.get("optional_preds")[1]
        specimen.save()
    else:
        logging.warning(f"Did not get a morphospecies_id for specimen_id={id}. Raw response: {data}")
    return


@celery_app.task(autoretry_for=(requests.RequestException,), soft_time_limit=240,
                 retry_kwargs={'max_retries': 3, 'countdown': 30},
                 retry_backoff=True)
def obj_det_image(specimenimage_id):
    if not settings.AI_INFERENCE_URL:
        return
    SpecimenImpage = apps.get_model(app_label='samples', model_name='SpecimenImage')
    try:
        specimenimage = SpecimenImpage.objects.get(id=specimenimage_id)
    except SpecimenImpage.DoesNotExist:
        logging.warning(f"DoesNotExist: SpecimenImage with id={specimenimage_id}")
        return
    try:
        files = {'file': specimenimage.image_thumbnail_large}
        response = requests.post(settings.AI_INFERENCE_URL + 'yolo-predict', files=files, timeout=10)
    except SoftTimeLimitExceeded:
        logging.exception('SoftTimeLimitExceeded on id_image of specimen id: {}'.format(specimenimage_id))
        return
    except FileNotFoundError as e:
        logging.warning(f"FileNotFoundError for specimenimage_id={specimenimage_id}: {e}")
        logging.info(f"Setting image_notfound=True for specimenimage_id={specimenimage_id}")
        specimenimage.image_notfound = True
        specimenimage.save()
    # dont make changes if we didnt get data
        return
    except Exception as e:
        logging.error(f"Error during YOLO prediction: {e}")
        return

    try:
        response.raise_for_status()
        response = response.json()
    except Exception as e:
        logging.error(f"Error parsing YOLO response for specimenimage_id={specimenimage_id}: {e}")
        return
    if not response:
        return
    if 'model_version' in response[0].keys():
        specimenimage.object_det_model_version = response[0]['model_version']
        # verify a object detection response
        if all([v in response[0].keys() for v in ['x', 'y', 'width', 'height']]):
            specimenimage.object_det_label = response
        else:
            specimenimage.object_det_label = []
    specimenimage.save()


# only run on Ecdysis01
@shared_task
def run_classify_new_images():
    if settings.ON_ECDYSIS_SERVER == 'YES':
        call_command('classify_new_images')


# only run on Ecdysis01
@shared_task
def run_update_classifications():
    if settings.ON_ECDYSIS_SERVER == 'YES':
        call_command('update_classifications')


# only run on Ecdysis01
@shared_task
def run_s3_media_download():
    if settings.ON_ECDYSIS_SERVER == 'YES':
        call_command('s3_download_images')


# only run on Ecdysis01
@shared_task
def run_set_public_images():
    if settings.ON_ECDYSIS_SERVER == 'YES':
        call_command('set_public_images')


# only run on Ecdysis01
@shared_task
def run_refresh_public_exports():
    if settings.ON_ECDYSIS_SERVER == 'YES':
        call_command('refresh_public_exports')
