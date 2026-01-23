from django.contrib.gis.geos import Point
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from ..core.constants import FIPS_STATE
from .models import UsCountiesTigerLine


@require_GET
def get_region_by_coordinates(request):
    try:
        lat = float(request.GET.get('lat'))
        lon = float(request.GET.get('lon'))
        point = Point(lon, lat, srid=4326)

        counties = UsCountiesTigerLine.objects.filter(geom__contains=point)
        if counties.count() == 1:
            county = counties.first()
            state_name = FIPS_STATE.get(county.statefp, '')
            return JsonResponse({'state': state_name, 'county': county.name})
    except Exception:
        pass

    return JsonResponse({'state': '', 'county': ''})
