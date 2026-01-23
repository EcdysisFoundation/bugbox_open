from django.contrib.auth.mixins import PermissionRequiredMixin
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework.viewsets import ModelViewSet

from bugbox3.core.permissions import IS_RESEARCH
from bugbox3.samples.constants import SERIALIZER_FIELDS_MUTIIMAGE
from bugbox3.samples.models import MultiSpecimenImage


class MultiSpecimenSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = MultiSpecimenImage
        fields = SERIALIZER_FIELDS_MUTIIMAGE + ['sample_id']


class MultiSpecimenViewSet(PermissionRequiredMixin, ModelViewSet):

    permission_required = IS_RESEARCH
    serializer_class = MultiSpecimenSerializer

    def get_queryset(self):
        sample_id = int(self.kwargs['sample_id'])
        return MultiSpecimenImage.objects.user_access(
            self.request.user).filter(sample_id=sample_id)
