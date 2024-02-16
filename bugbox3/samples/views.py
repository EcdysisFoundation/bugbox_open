from django.views.generic import TemplateView
from django.contrib.postgres.search import SearchVector
from rest_framework.viewsets import ReadOnlyModelViewSet

from rest_framework.response import Response

from .models import Experiment
from .serializers import ExperimentsDatatablesSerializer
from . import constants


class ExperimentsDatatablesViewSet(ReadOnlyModelViewSet):
    serializer_class = ExperimentsDatatablesSerializer

    queryset = Experiment.objects.all().order_by(constants.FIELD_NAME)
    
    def filter_for_datatable(self, queryset):
        # filtering
        search_vector = [constants.FIELD_NAME, constants.FIELD_ABBREVIATION]
        search_query = self.request.query_params.get('search[value]')
        if search_query:
            queryset = queryset.annotate(
                search=SearchVector(*search_vector)
            ).filter(search=search_query)
        return queryset

    def list(self, request, *args, **kwargs):
        draw = request.query_params.get('draw')
        queryset = self.filter_queryset(self.get_queryset())
        recordsTotal = queryset.count()
        filtered_queryset = self.filter_for_datatable(queryset)
        try:
            start = int(request.query_params.get('start'))
        except:
            start = 0
        try:
            length = int(request.query_params.get('length'))
        except:
            length = 10
        end = length + start
        serializer = self.get_serializer(filtered_queryset[start:end], many=True)
        response = {
            'draw': draw,
            'recordsTotal': recordsTotal,
            'recordsFiltered': filtered_queryset.count(),
            'data': serializer.data
        }
        return Response(response)

class ExperimentsView(TemplateView):
    template_name = 'samples/experiments.html'

class SpecimensView(TemplateView):
    template_name = 'samples/specimens.html'