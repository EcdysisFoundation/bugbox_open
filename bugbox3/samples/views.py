from django.views.generic import TemplateView
from rest_framework.viewsets import ReadOnlyModelViewSet


class ExperimentsView(TemplateView):
    template_name = 'samples/experiments.html'

class SpecimensView(TemplateView):
    template_name = 'samples/specimens.html'