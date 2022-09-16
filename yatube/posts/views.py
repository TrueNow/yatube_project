from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.views.generic.list import MultipleObjectMixin

from .forms import PostForm
from .models import Post, Group


User = get_user_model()
PAGINATE_BY: int = 10


class IndexView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'posts/index.html'
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return self.model.objects.select_related('author', 'group')


class PostsGroupView(DetailView, MultipleObjectMixin):
    model = Group
    slug_url_kwarg = 'group_slug'
    slug_field = 'slug'
    context_object_name = 'group'
    template_name = 'posts/group_list.html'
    paginate_by = PAGINATE_BY

    def get_context_data(self, *, object_list=None, **kwargs):
        return super().get_context_data(
            object_list=self.object.posts.select_related('author'),
            **kwargs
        )


class ProfileView(DetailView, MultipleObjectMixin):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'author'
    template_name = 'posts/profile.html'
    paginate_by = PAGINATE_BY

    def get_context_data(self, *, object_list=None, **kwargs):
        return super().get_context_data(
            object_list=self.object.posts.select_related('group'),
            **kwargs
        )


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'
    template_name = 'posts/post_detail.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/create_post.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return redirect('posts:profile', username=self.request.user.username)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'
    template_name = 'posts/create_post.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if request.user != self.object.author:
            return redirect('posts:post_detail', post_id=self.object.pk)
        return response
