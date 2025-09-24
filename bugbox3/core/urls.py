from django.urls import path

from ..users.views import EulaReadView, EulaView
from .views import (LookupChoicesCreateView, LookupChoicesDeleteView,
                    LookupChoicesUpdateView, LookupChoicesView,
                    OrgMemberDeleteView, OrgMembersView)
from .stitcher_views import StitcherUpdateView, StitcherView

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
    path('org-members/<int:org_id>', OrgMembersView.as_view(), name='org-members'),
    path('member-delete/<int:id>/<int:org_id>', OrgMemberDeleteView.as_view(), name='member-delete'),
    path('stitcher', StitcherView.as_view(), name='stitcher'),
    path('stitcher-form/<uuid:guid>', StitcherUpdateView.as_view(), name='stitcher-form')
]
