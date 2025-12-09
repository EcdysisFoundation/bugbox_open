import os
from io import BytesIO
from pathlib import Path
from PIL import Image
from uuid import uuid4

from django.core.files import File
from django.core.files.storage import default_storage


def crop_and_save_images(image, bounding_boxes):
    """
    Crops images based on a list of bounding boxes and saves them to a directory.
    """
    result = []
    original_max_pixels = Image.MAX_IMAGE_PIXELS
    if not original_max_pixels:
        raise ValueError('MAX_IMAGE_PIXELS was not set')
    Image.MAX_IMAGE_PIXELS = None

    image_types = {
        'jpg': 'JPEG',
        'jpeg': 'JPEG',
        'png': 'PNG',
    }
    supported_extension = [v for v in image_types.keys()]
    img_suffix = Path(image.file.name).name.split(".")[-1]
    img_basename = Path(image.file.name).name.split(".")[:-1]

    with Image.open(image) as img:
        if img_suffix.lower() in supported_extension:
            img_format = image_types[img_suffix.lower()]
        else:
            return result

        for i, bbox in enumerate(bounding_boxes):
            try:
                x_min, y_min, x_max, y_max = map(int, bbox)
                img_width, img_height = img.size
                x_min = max(0, x_min)
                y_min = max(0, y_min)
                x_max = min(img_width, x_max)
                y_max = min(img_height, y_max)

                cropped_image = img.crop((x_min, y_min, x_max, y_max))
                output_filename = f"{img_basename}_crop_{i}.{img_suffix}"
                buffer = BytesIO()
                cropped_image.save(buffer, format=img_format)
                file_object = File(buffer, name=output_filename)
                result.append((file_object, i))
            except (ValueError, IndexError) as e:
                print(f"Skipping invalid bounding box {bbox}: {e}")
    Image.MAX_IMAGE_PIXELS = original_max_pixels
    return result


def convert_coco_bbox_to_pil(bbox):
    # convert coco formatted bounding box to PIL format
    x, y, width, height = bbox
    x_min = x
    y_min = y
    x_max = x + width
    y_max = y + height
    return (x_min, y_min, x_max, y_max)


def convert_ls_to_coco_to_pil(bbox, image_width, image_height):
    # undo format_result_label_studio() formatted boundingbox
    x, y, width, height = bbox
    x = x / 100 * image_width
    y = y / 100 * image_height
    width = width / 100 * image_width
    height = height / 100 * image_height
    return convert_coco_bbox_to_pil((x, y, width, height))


def crop_img_to_annotations(image, anno):
    if not default_storage.exists(image.name):
        return None
    static_bboxes = [
        convert_ls_to_coco_to_pil(
            (v['x'], v['y'], v['width'], v['height']),
            v['original_width'],
            v['original_height']) for v in anno
    ]
    bytes_imgs = crop_and_save_images(image, static_bboxes)
    return bytes_imgs


def create_segmentation(
    label, segmentation, image_height, image_width
):
    """
    FROM: https://github.com/HumanSignal/label-studio-sdk/blob/master/src/label_studio_sdk/converter/imports/coco.py#L78C5-L78C24
    Convert COCO segmentation annotation to Label Studio polygon format.

    COCO segmentation format: flat array of [x1,y1,x2,y2,...] coordinates
    Label Studio format: array of [x,y] points as percentages

    Args:
        label (txt): label for object
        segmentation (list): Flat list of polygon coordinates [x1,y1,x2,y2,...]
        from_name (str): Control tag name from Label Studio labeling config
        image_height (int): Height of the source image in pixels
        image_width (int): Width of the source image in pixels
        to_name (str): Object name from Label Studio labeling config

    Returns:
        dict: Label Studio polygon annotation item
    """
    # Convert flat array [x1,y1,x2,y2,...] to array of points [[x1,y1],[x2,y2],...]
    points = [list(x) for x in zip(*[iter(segmentation)] * 2)]

    # Convert absolute coordinates to percentages
    for i in range(len(points)):
        points[i][0] = points[i][0] / image_width * 100.0
        points[i][1] = points[i][1] / image_height * 100.0

    item = {
        "id": uuid4().hex[0:10],
        "type": "polygonlabels",
        "value": {"points": points, "polygonlabels": [label]},
        "to_name": "image",
        "from_name": "label",
        "image_rotation": 0,
        "original_width": image_width,
        "original_height": image_height,
    }
    return item
