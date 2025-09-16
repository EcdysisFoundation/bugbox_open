from django.http import Http404
from django.contrib.auth.decorators import permission_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from bugbox3.samples.models import Sample
from .permissions import IS_RESEARCH
# from .stitcher_utils import convert_ls_to_coco_to_pil, crop_and_save_images


