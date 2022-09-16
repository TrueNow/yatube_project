from django.db.models import QuerySet
from django.shortcuts import reverse, get_object_or_404
from http import HTTPStatus

from .test import PostsTestCase
from ..models import Post
from ..views import PAGINATE_BY


class PostsViewsTests(PostsTestCase):
    @staticmethod
    def count_posts(author=None, group=None):
        if author is not None:
            return author.posts.count()
        if group is not None:
            return group.posts.count()
        return Post.objects.count()

    def check_paginator(self, client, page, author=None, group=None):
        """
        Проверка paginator на странице.
            Если страница конкретного пользователя -> указать author.
            Если страница конкретной группы -> указать group.
        """
        COUNT_POSTS_ON_PAGE: list = []

        count_posts = self.count_posts(author, group)
        for i in range(count_posts // PAGINATE_BY):
            COUNT_POSTS_ON_PAGE.append(PAGINATE_BY)
        COUNT_POSTS_ON_PAGE.append(count_posts % PAGINATE_BY)

        error_message: str = 'Число постов на странице не равно {}'

        for i, count_posts in enumerate(COUNT_POSTS_ON_PAGE):
            response = client.get(page + f'?page={i + 1}')
            self.assertEqual(
                response.context['object_list'].count(),
                count_posts,
                error_message.format(count_posts)
            )

    def test_index_page(self):
        """Тест главной страницы."""
        client = self.client_anonymous
        name = 'posts:index'
        kwargs = {}
        template = 'posts/index.html'

        page = reverse(name, kwargs=kwargs)
        self.check_paginator(client, page)

        response = client.get(page)
        self.assertTemplateUsed(response, template)
        posts = response.context.get('posts')
        self.assertIsInstance(posts, QuerySet)

        for post in posts:
            with self.subTest(post=post):
                self.assertIsInstance(post, Post)

    def test_group_list_page(self):
        """Тест страницы группы."""
        group = self.group
        client = self.client_anonymous
        name = 'posts:group_list'
        kwargs = {'group_slug': group.slug}
        template = 'posts/group_list.html'

        page = reverse(name, kwargs=kwargs)
        self.check_paginator(client, page, group=group)

        response = client.get(page)
        self.assertTemplateUsed(response, template)
        response_group = response.context.get('group')
        self.assertEqual(response_group, group)

        posts = response.context.get('object_list')
        for post in posts:
            with self.subTest(post=post):
                self.assertEqual(post.group, group)

    def test_profile_page(self):
        """Тест страницы профиля автора."""
        author = self.author
        client = self.client_anonymous
        name = 'posts:profile'
        kwargs = {'username': author.username}
        template = 'posts/profile.html'

        page = reverse(name, kwargs=kwargs)
        self.check_paginator(client, page, author=author)

        response = client.get(page)
        self.assertTemplateUsed(response, template)
        response_author = response.context.get('author')
        self.assertEqual(response_author, author)

        posts = response.context.get('object_list')
        for post in posts:
            with self.subTest(post=post):
                self.assertEqual(post.author, author)

    def test_post_detail_page(self):
        """Тест страницы выбранного поста."""
        post = self.post
        client = self.client
        name = 'posts:post_detail'
        kwargs = {'post_id': post.pk}
        template = 'posts/post_detail.html'

        page = reverse(name, kwargs=kwargs)

        response = client.get(page)
        self.assertTemplateUsed(response, template)
        response_post = response.context.get('post')
        self.assertEqual(response_post, post)

    def test_post_create_page(self):
        """Тест страницы создания нового поста."""
        user = self.author
        group = self.group
        client = self.client_author
        name = 'posts:post_create'
        kwargs = {}
        template = 'posts/create_post.html'

        page = reverse(name, kwargs=kwargs)

        response = client.get(page)
        self.assertTemplateUsed(response, template)

        count_posts_before_add = Post.objects.count()
        new_post_data = {
            'text': 'Новый пост',
            'group': group.pk
        }
        response = client.post(page, data=new_post_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': user.username}
            )
        )
        count_posts_after_add = Post.objects.count()
        self.assertEqual(
            count_posts_after_add,
            count_posts_before_add + 1,
        )

        self.assertTrue(
            get_object_or_404(
                Post,
                text=new_post_data.get('text'),
                group=new_post_data.get('group'),
                author=user,
            )
        )

    def test_post_edit_page(self):
        """Тест страницы редактирования нового поста."""
        post = self.post
        client = self.client_author
        name = 'posts:post_edit'
        kwargs = {'post_id': post.pk}
        template = 'posts/create_post.html'

        page = reverse(name, kwargs=kwargs)

        response = client.get(page)
        self.assertTemplateUsed(response, template)
        response_post = response.context.get('post')
        self.assertEqual(response_post, post)

        count_posts_before_edit = Post.objects.count()
        new_post_data = {
            'text': 'Отредактированный пост',
            'group': post.group.pk
        }
        response = client.post(page, data=new_post_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.pk}
            )
        )
        count_posts_after_edit = Post.objects.count()
        self.assertEqual(
            count_posts_after_edit,
            count_posts_before_edit,
        )

        self.assertTrue(
            get_object_or_404(
                Post,
                text=new_post_data.get('text'),
                group=new_post_data.get('group'),
                author=post.author,
            )
        )
