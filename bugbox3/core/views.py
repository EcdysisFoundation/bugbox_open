from django.contrib.postgres.search import SearchVector
from rest_framework.response import Response


class DatatablesModelViewSetMixin:
    """
    For use with ViewSet such as ReadOnlyModelViewSet and datatables.
    In ViewSet, proved a serializer_class and a get_queryset or queryset
    and optionally a search_vector for filtering.
    """

    search_vector = []

    def filter_for_datatable(self, queryset):
        if self.search_vector:
            search_query = self.request.query_params.get('search[value]')
            if search_query:
                queryset = queryset.annotate(
                    search=SearchVector(*self.search_vector)
                ).filter(search=search_query)
        return queryset
    
    def list(self, request, *args, **kwargs):
        draw = request.query_params.get('draw')
        queryset = self.filter_queryset(self.get_queryset())
        recordsTotal = queryset.count()
        filtered_queryset = self.filter_for_datatable(queryset)
        try:
            start = int(request.query_params.get('start'))
        except ValueError:
            start = 0
        try:
            length = int(request.query_params.get('length'))
        except ValueError:
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