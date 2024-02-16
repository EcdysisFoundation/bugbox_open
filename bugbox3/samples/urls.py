from django.urls import path

from .views import ExperimentsView, SpecimensView


app_name = "samples"
urlpatterns = [
    path('experiments/', ExperimentsView.as_view(), name='experiments'),
    path('specimens/', SpecimensView.as_view(), name='specimens'),
]