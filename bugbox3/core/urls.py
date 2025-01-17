from django.urls import path

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
    )
]
