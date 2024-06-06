import json
from io import BytesIO
from pathlib import Path

from django.core.files import File
from django.core.serializers.json import DjangoJSONEncoder
from PIL import Image


def encode_json(data):
    return json.dumps(data, cls=DjangoJSONEncoder)


def get_json_context(context_dict):
    if isinstance(context_dict, dict):
        thejson = encode_json(context_dict)
        return '<script id="json_context" type="application/json">%s</script>' % thejson
    else:
        return None


IMAGE_TYPES = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
}


def resized_thumbnail(image, width, height, thumbname='thumbnail'):
    # Open the image using Pillow
    with Image.open(image) as img:
        output_size = (width, height)
        # Create a new resized “thumbnail” version of the image with Pillow
        img.thumbnail(output_size)
        # Find the file name of the image
        img_filename = Path(image.file.name).name
        # Spilt the filename on “.” to get the file extension only
        img_suffix = Path(image.file.name).name.split(".")[-1]
        new_filename = '{0}_{1}.{2}'.format(str(img_filename[:-len(img_suffix)-1]), str(thumbname), str(img_suffix))
        # Use the file extension to determine the file type from the image_types dictionary
        img_format = IMAGE_TYPES[img_suffix.lower()]
        # Save the resized image into the buffer, noting the correct file type
        buffer = BytesIO()
        img.save(buffer, format=img_format)
        # Wrap the buffer in File object
        file_object = File(buffer, name=new_filename)
        # return the new resized
        return file_object
