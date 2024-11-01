import json
from io import BytesIO
from pathlib import Path

import boto3
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.serializers.json import DjangoJSONEncoder
from PIL import Image

from ..samples.constants import IMAGE_GRID_CHOICE_4_BY_3

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


def grid_id_format(v):
    return '-grid-i-[{0}]'.format(v)


def get_media_url(file):
    """
    Get media file urls
    """
    if settings.MEDIA_URL == '/media/':
        # assume local storage
        return file.url
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


def resized_thumbnail(image, width, height, thumbname='thumbnail'):
    # Open the image using Pillow
    if default_storage.exists(image.name):
        try:
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
                buffer = BytesIO()
                img.save(buffer, format=img_format)
                # Wrap the buffer in File object
                file_object = File(buffer, name=new_filename)
                # return the new resized
                return file_object
        except Exception:
            print('Warning: Exception encountered for file {}'.format(image.path))
    else:
        return None


def crop_img_to_grid(image, grid):
    """
    Return list of [(cropped_image, index),] from image cropped to grid.
    Where index is the position in the grid.
    """

    if default_storage.exists(image.name):
        # Find the file name of the image
        img_filename = Path(image.file.name).name
        # Spilt the filename on “.” to get the file extension only
        img_suffix = Path(image.file.name).name.split(".")[-1]
        img_format = IMAGE_TYPES[img_suffix.lower()]
        width, height = image.width, image.height
        with Image.open(image) as img:
            if grid == IMAGE_GRID_CHOICE_4_BY_3:
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
