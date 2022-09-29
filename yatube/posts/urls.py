from django.urls import path

from . import views


app_name = 'posts'

urlpatterns = [
    path(
        '',
        views.index_view,
        name='index'
    ),
    path(
        'follow/',
        views.follow_view,
        name='follow'
    ),
    path(
        'group/<slug:group_slug>/',
        views.group_detail_view,
        name='group_detail'
    ),
    path(
        'profile/<str:username>/',
        views.profile_detail_view,
        name='profile_detail'
    ),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
    path(
        'create/',
        views.post_create_view,
        name='post_create'
    ),
    path(
        'posts/<int:post_id>/',
        views.post_detail_view,
        name='post_detail'
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.post_comment,
        name='post_comment'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.post_edit_view,
        name='post_edit'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.post_delete,
        name='post_delete'
    )
]
