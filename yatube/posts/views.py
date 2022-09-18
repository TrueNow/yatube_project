from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import generic
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin
from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow, Comment

PAGINATE_BY: int = 10


class IndexView(generic.ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'posts/index.html'
    paginate_by = PAGINATE_BY


class FollowIndexView(LoginRequiredMixin, generic.ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'posts/follow.html'
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        authors = [
            follow.author
            for follow in Follow.objects.filter(user=self.request.user)
        ]
        return Post.objects.filter(author__in=authors)


class GroupDetailView(generic.DetailView, MultipleObjectMixin):
    model = Group
    slug_url_kwarg = 'group_slug'
    slug_field = 'slug'
    context_object_name = 'group'
    template_name = 'posts/group_list.html'
    paginate_by = PAGINATE_BY

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            object_list=Post.objects.filter(group=self.object),
            **kwargs
        )
        return context


class ProfileDetailView(generic.DetailView, MultipleObjectMixin):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'author'
    template_name = 'posts/profile.html'
    paginate_by = PAGINATE_BY

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(
            object_list=Post.objects.filter(author=self.object),
            **kwargs
        )
        context['following'] = Follow.objects.filter(
            user=self.request.user,
            author=self.object,
        )
        return context


class PostDetailView(generic.DetailView, FormMixin):
    model = Post
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'
    template_name = 'posts/post_detail.html'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(post=context.get('post'))
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = self.object
        comment.save()
        return redirect('posts:post_detail', post_id=self.object.pk)


class PostCreateView(LoginRequiredMixin, generic.CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/create_post.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return redirect('posts:profile', username=self.request.user.username)


class PostUpdateView(LoginRequiredMixin, generic.UpdateView):
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


class FollowProfileView(LoginRequiredMixin, ProfileDetailView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user != self.object:
            Follow.objects.create(user=request.user, author=self.object)
        return redirect('posts:profile', self.object.username)


class UnfollowProfileView(LoginRequiredMixin, ProfileDetailView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user != self.object:
            Follow.objects.get(user=request.user, author=self.object).delete()
        return redirect('posts:profile', self.object.username)
