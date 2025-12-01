import json
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import boto3
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.serializers.json import DjangoJSONEncoder
from django.core.files.images import get_image_dimensions
from PIL import Image

from bugbox3.samples import constants


S3_CLIENT = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )


def encode_json(data):
    return json.dumps(data, cls=DjangoJSONEncoder)


def get_json_context(context_dict):
    if isinstance(context_dict, dict):
        thejson = encode_json(context_dict)
        return '<script id="json_context" type="application/json">%s</script>' % thejson
    else:
        return None


def get_filename_org_timestamp(title, org_id, ext):
    """
    Return a filename formated with title, organization_id, and file extension.
    """
    now = datetime.now(tz=timezone.utc)
    filename = '__'.join([title, str(org_id),
                          now.strftime('%Y-%m-%d_%H%M%S')])
    return '{0}.{1}'.format(filename, ext)


def grid_id_format(v):
    return '-grid-i-[{0}]'.format(v)


def get_media_url(file, public=False):
    """
    Get media file urls
    """
    if not file:
        return ''
    if settings.MEDIA_URL == '/media/':
        # assume local storage
        return file.url
    if public:
        # if for example SpecimenImage.public_image = True, pass it in
        # requires acl='public-read' on S3 object
        return settings.MEDIA_URL + file.name
    return S3_CLIENT.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME_MEDIA,
                'Key': file.name},
        HttpMethod="GET",
        ExpiresIn=3600)


IMAGE_TYPES = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
}


def resized_thumbnail(image, width, height, buffer, thumbname='thumbnail', large_ok=False):
    # Open the image using Pillow
    if default_storage.exists(image.name):
        try:
            if large_ok:
                original_max_pixels = Image.MAX_IMAGE_PIXELS
                if not original_max_pixels:
                    raise ValueError('MAX_IMAGE_PIXELS was not set')
                Image.MAX_IMAGE_PIXELS = None
            with Image.open(image) as img:
                output_size = (width, height)
                # Create a new resized “thumbnail” version of the image with Pillow
                img.thumbnail(output_size)
                # Find the file name of the image
                img_filename = Path(image.file.name).name
                # Spilt the filename on “.” to get the file extension only
                img_suffix = Path(image.file.name).name.split(".")[-1]
                new_filename = '{0}_{1}.{2}'.format(
                    str(img_filename[:-len(img_suffix)-1]), str(thumbname), str(img_suffix))
                # Use the file extension to determine the file type from the image_types dictionary
                img_format = IMAGE_TYPES[img_suffix.lower()]
                # Save the resized image into the buffer, noting the correct file type
                img.save(buffer, format=img_format)
                # Wrap the buffer in File object
                file_object = File(buffer, name=new_filename)
                # return the new resized
                return file_object
        except Exception as e:
            warn = 'Warning: Exception encountered in resized_thumbnail for file'
            print('{0} {1} {2}'.format(warn, image.name, e))
        finally:
            if large_ok:
                Image.MAX_IMAGE_PIXELS = original_max_pixels

    else:
        return None


def crop_img_to_grid(image, grid):
    """
    Return list of [(cropped_image, index),] from image cropped to grid.
    Where index is the position in the grid.
    TODO: Use of BytesIO in this way may cause memory leak. Is it closed when done?
    """

    if default_storage.exists(image.name):
        # Find the file name of the image
        img_filename = Path(image.file.name).name
        # Spilt the filename on “.” to get the file extension only
        img_suffix = Path(image.file.name).name.split(".")[-1]
        img_format = IMAGE_TYPES[img_suffix.lower()]
        width, height = image.width, image.height
        with Image.open(image) as img:
            if grid == constants.IMAGE_GRID_CHOICE_4_BY_3:
                grid_params = [
                    [0, 0, width * (1/4), height * (1/3)],
                    [width * (1/4), 0, width * (2/4), height * (1/3)],
                    [width * (2/4), 0, width * (3/4), height * (1/3)],
                    [width * (3/4), 0, width * (4/4), height * (1/3)],
                    [0, height * (1/3), width * (1/4), height * (2/3)],
                    [width * (1/4), height * (1/3), width * (2/4), height * (2/3)],
                    [width * (2/4), height * (1/3), width * (3/4), height * (2/3)],
                    [width * (3/4), height * (1/3), width * (4/4), height * (2/3)],
                    [0, height * (2/3), width * (1/4), height * (3/3)],
                    [width * (1/4), height * (2/3), width * (2/4), height * (3/3)],
                    [width * (2/4), height * (2/3), width * (3/4), height * (3/3)],
                    [width * (3/4), height * (2/3), width * (4/4), height * (3/3)],
                ]
            else:
                # no other supported grid_params
                return None

            result = []
            for i, params in enumerate(grid_params):
                new_filename = '{0}{1}.{2}'.format(
                    str(img_filename[:-len(img_suffix)-1]),
                    grid_id_format(i),
                    str(img_suffix))

                crop_image = img.crop(params)
                buffer = BytesIO()
                crop_image.save(buffer, format=img_format)
                # Wrap the buffer in File object
                file_object = File(buffer, name=new_filename)
                result.append((file_object, i))
        return result
    return None


def save_specimen_img_thumbs(instance):
    """
    If a thumbnail size doesnt exist, make it.
    If they all exist, do as little as possible.
    """
    a = None
    b = None
    c = None
    needs_save = False
    dims = get_image_dimensions(instance.image)
    if dims[0] and dims[1]:
        instance.image_width = dims[0]
        instance.image_height = dims[1]
        needs_save = True
    
    if not instance.image_thumbnail and dims[0] > constants.SPECIMEN_IMAGE_THUMBSIZE:
        a = BytesIO()
        instance.image_thumbnail = resized_thumbnail(
            instance.image,
            constants.SPECIMEN_IMAGE_THUMBSIZE,
            constants.SPECIMEN_IMAGE_THUMBSIZE,
            a)
        needs_save = True
    if not instance.image_thumbnail_medium and dims[0] > constants.SPECIMEN_IMAGE_THUMBSIZE_MEDIUM:
        b = BytesIO()
        instance.image_thumbnail_medium = resized_thumbnail(
            instance.image,
            constants.SPECIMEN_IMAGE_THUMBSIZE_MEDIUM,
            constants.SPECIMEN_IMAGE_THUMBSIZE_MEDIUM,
            b, 'thumbnail_medium')
        needs_save = True
    if not instance.image_thumbnail_large and dims[0] > constants.SPECIMEN_IMAGE_THUMBSIZE_LARGE:
        c = BytesIO()
        instance.image_thumbnail_large = resized_thumbnail(
            instance.image,
            constants.SPECIMEN_IMAGE_THUMBSIZE_LARGE,
            constants.SPECIMEN_IMAGE_THUMBSIZE_LARGE,
            c, 'thumbnail_large')
        needs_save = True
    
    if instance.image_thumbnail_large:
        thumb_dims = get_image_dimensions(instance.image_thumbnail_large)
        if thumb_dims[0] and thumb_dims[1]:
            instance.image_thumbnail_large_width = thumb_dims[0]
            instance.image_thumbnail_large_height = thumb_dims[1]
            needs_save = True
    
    if needs_save:
        instance.save()
    
    for i in (a, b, c):
        if i:
            i.close()
    
    return


def uniform_time_display(date_time):
    return date_time.strftime('%B %d, %Y, %I:%M %p')


def cast_utc_time(utc_string):
    utc_format = "%Y-%m-%dT%H:%M:%S.%f"
    try:
        naive_dt = datetime.strptime(utc_string, utc_format)
        return naive_dt
    except Exception:
        return utc_string
