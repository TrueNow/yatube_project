from django.urls import path
from django.views.decorators.cache import cache_page

from . import views


app_name = 'posts'

urlpatterns = [
    path(
        '',
        cache_page(20)(views.IndexView.as_view()),
        name='index'
    ),
    path(
        'follow/',
        views.FollowView.as_view(),
        name='follow'
    ),
    path(
        'group/<slug:group_slug>/',
        views.GroupDetailView.as_view(),
        name='group_detail'
    ),
    path(
        'profile/<str:username>/',
        views.ProfileDetailView.as_view(),
        name='profile_detail'
    ),
    path(
        'profile/<str:username>/follow/',
        views.ProfileFollowView.as_view(),
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.ProfileUnfollowView.as_view(),
        name='profile_unfollow'
    ),
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'create/',
        views.PostCreateView.as_view(),
        name='post_create'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostEditView.as_view(),
        name='post_edit'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='post_delete'
    )
]
