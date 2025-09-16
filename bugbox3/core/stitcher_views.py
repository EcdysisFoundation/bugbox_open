from django.http import Http404
from django.contrib.auth.decorators import permission_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from bugbox3.samples.models import Sample
from .permissions import IS_RESEARCH
# from .stitcher_utils import convert_ls_to_coco_to_pil, crop_and_save_images


@require_POST
@permission_required(IS_RESEARCH)
def crop_and_save_pano(request, guid, sample_id):
    print(request)
    try:
        sample = Sample.objects.user_access(request.user).get(id=sample_id)
    except Sample.DoesNotExist:
        raise Http404
    message = f"Image was sent to be processed to Sample ID: {sample_id}, guid: {guid}"
    print(message)
    return HttpResponse(message)
