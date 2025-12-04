from django.urls import path
from whatsapp_groups import views
from whatsapp_groups import webhooks

urlpatterns = [
    path('groups/', views.create_group, name='create-group'),
    path('groups/list/', views.list_groups, name='list-groups'),
    path('groups/<int:group_id>/', views.get_group, name='get-group'),
    path('groups/<int:group_id>/join-requests/', views.get_group_join_requests, name='get-group-join-requests'),
    path('groups/<int:group_id>/join-requests/approve/', views.approve_group_join_requests, name='approve-group-join-requests'),
    path('groups/<int:group_id>/join-requests/reject/', views.reject_group_join_requests, name='reject-group-join-requests'),
    path('webhooks/group-lifecycle/', webhooks.group_lifecycle_webhook, name='group-lifecycle-webhook'),
]

