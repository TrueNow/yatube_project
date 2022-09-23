from django.db.models import QuerySet
from django.db.models.fields.files import ImageFieldFile
from django.shortcuts import get_object_or_404
from http import HTTPStatus

from .test import *
from ..models import Post, Comment, Follow
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

    def test_index_cache(self):
        client = self.client_author

        page = INDEX_PAGE

        response = client.get(page)
        posts = response.context.get('posts')
        self.assertIsInstance(posts, QuerySet)
        post = Post.objects.get(id=4)
        print('\n***********')
        print(posts)
        print('-------------')
        print(post)
        print('----------------')
        client.get(POST_DELETE_PAGE(post.pk))
        response = client.get(page)
        posts = response.context.get('posts')
        self.assertIn(post, posts)
        print(posts)
        print('**************')

    def test_index_page(self):
        """Тест главной страницы."""
        client = self.client
        template = 'posts/index.html'

        page = INDEX_PAGE
        self.check_paginator(client, page)

        response = client.get(page)
        self.assertTemplateUsed(response, template)
        posts = response.context.get('posts')
        self.assertIsInstance(posts, QuerySet)

        for post in posts:
            with self.subTest(post=post):
                self.assertIsInstance(post, Post)
                self.assertIsInstance(post.image, ImageFieldFile)

    def test_follow_page(self):
        """Тест ленты."""
        user = self.user
        author = self.author
        client = self.client_user
        template = 'posts/index.html'

        client.get(PROFILE_FOLLOW(author.username))
        self.assertTrue(get_object_or_404(Follow, user=user, author=author))

        page = FOLLOW_PAGE
        self.check_paginator(client, page)

        response = client.get(page)
        self.assertTemplateUsed(response, template)
        posts = response.context.get('posts')
        self.assertIsInstance(posts, QuerySet)

        authors = [
            follow.author
            for follow in Follow.objects.filter(user=user)
        ]
        posts_db = Post.objects.filter(author__in=authors)
        for post in posts:
            with self.subTest(post=post.pk):
                self.assertIn(post, posts_db)
        client.get(PROFILE_UNFOLLOW(author.username))

    def test_group_list_page(self):
        """Тест страницы группы."""
        group = self.group
        client = self.client
        template = 'posts/group_detail.html'

        page = GROUP_PAGE(group.slug)
        self.check_paginator(client, page, group=group)

        response = client.get(page)
        self.assertTemplateUsed(response, template)
        response_group = response.context.get('group')
        self.assertEqual(response_group, group)

        posts = response.context.get('object_list')
        for post in posts:
            with self.subTest(post=post):
                self.assertEqual(post.group, group)
                self.assertIsInstance(post.image, ImageFieldFile)

    def test_profile_page(self):
        """Тест страницы профиля автора."""
        author = self.author
        client = self.client
        template = 'posts/profile_detail.html'

        page = PROFILE_PAGE(author.username)
        self.check_paginator(client, page, author=author)

        response = client.get(page)
        self.assertTemplateUsed(response, template)
        response_author = response.context.get('author')
        self.assertEqual(response_author, author)

        posts = response.context.get('object_list')
        for post in posts:
            with self.subTest(post=post):
                self.assertEqual(post.author, author)
                self.assertIsInstance(post.image, ImageFieldFile)

    def test_post_detail_page(self):
        """Тест страницы выбранного поста."""
        post = self.post
        user = self.user
        clients = (self.client, self.client_user)
        template = 'posts/post_detail.html'

        page = POST_DETAIL_PAGE(post.pk)

        response = self.client.get(page)
        self.assertTemplateUsed(response, template)
        response_post = response.context.get('post')
        self.assertEqual(response_post, post)
        self.assertIsInstance(response_post.image, ImageFieldFile)

        # Анонимный клиент
        new_comment_data = {
            'text': 'Новый комментарий',
        }
        for client in clients:
            count_comments_before = Comment.objects.filter(post=post).count()
            response = client.post(page, data=new_comment_data)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            self.assertRedirects(
                response,
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': post.pk}
                )
            )
            count_comments_after = Comment.objects.filter(post=post).count()
            if client == clients[1]:
                count_comments_after -= 1
            self.assertEqual(
                count_comments_before,
                count_comments_after
            )

        self.assertTrue(
            get_object_or_404(
                Comment,
                post=post,
                author=user,
                text=new_comment_data.get('text'),
            )
        )

    def test_post_create_page(self):
        """Тест страницы создания нового поста."""
        user = self.author
        group = self.group
        client = self.client_author
        template = 'posts/create_post.html'

        page = POST_CREATE_PAGE

        response = client.get(page)
        self.assertTemplateUsed(response, template)

        new_post_data = {
            'text': 'Новый пост',
            'group': group.pk,
            'image': 'img/logo.png'
        }
        count_posts_before = Post.objects.count()
        response = client.post(page, data=new_post_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        count_posts_after = Post.objects.count()
        self.assertRedirects(response, PROFILE_PAGE(user.username))
        self.assertEqual(count_posts_before, count_posts_after - 1)

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
        template = 'posts/create_post.html'

        page = POST_EDIT_PAGE(post.pk)

        response = self.client_author.get(page)
        self.assertTemplateUsed(response, template)
        response_post = response.context.get('post')
        self.assertEqual(response_post, post)

        new_post_data = {
            'text': 'Отредактированный пост',
            'group': post.group.pk
        }
        count_posts_before = Post.objects.count()
        response = client.post(page, data=new_post_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        count_posts_after = Post.objects.count()
        self.assertRedirects(response, POST_DETAIL_PAGE(post.pk))
        self.assertEqual(count_posts_after, count_posts_before)

        self.assertTrue(
            get_object_or_404(
                Post,
                text=new_post_data.get('text'),
                group=new_post_data.get('group'),
                author=post.author,
            )
        )
