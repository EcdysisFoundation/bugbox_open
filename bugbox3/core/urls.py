from django.urls import path

from ..users.views import EulaReadView, EulaView
from .views import (LookupChoicesCreateView, LookupChoicesDeleteView,
                    LookupChoicesUpdateView, LookupChoicesView)

app_name = "core"
urlpatterns = [
    path('lookup-choices/<int:org_id>', LookupChoicesView.as_view(), name='lookup-choices'),
    path(
        'lookup-choices-create/<field>/<int:org_id>',
        LookupChoicesCreateView.as_view(),
        name='lookup-choices-create'
    ),
    path(
        'lookup-choices-update/<int:id>',
        LookupChoicesUpdateView.as_view(),
        name='lookup-choices-update'
    ),
    path(
        'lookup-choices-delete/<int:id>',
        LookupChoicesDeleteView.as_view(),
        name='lookup-choices-delete'
    ),
    path('eula/', view=EulaView.as_view(), name='eula'),
    path('read-eula/', view=EulaReadView.as_view(), name='read-eula'),
]
