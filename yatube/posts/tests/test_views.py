from http import HTTPStatus
from typing import List

from django.core.cache import cache
from django.db.models.fields.files import ImageFieldFile
from django.shortcuts import get_object_or_404

from .test import PostsTestCase
from posts.models import Post, Comment, Follow
from posts.utils import PAGINATE_BY


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

        for i, count_posts in enumerate(COUNT_POSTS_ON_PAGE):
            response = client.get(page + f'?page={i + 1}')
            count_response_posts = len(
                response.context['page_obj'].object_list
            )
            self.assertEqual(
                count_response_posts,
                count_posts,
                'Число постов на странице {} != {}'.format(
                    count_response_posts, count_posts
                )
            )

    def test_index_page(self):
        """Тест главной страницы."""
        cache.clear()
        client = self.client
        template = 'posts/index.html'

        page = self.INDEX_PAGE
        self.check_paginator(client, page)

        response = client.get(page)
        self.assertTemplateUsed(
            response,
            template,
            'Используется другой шаблон'
        )
        posts = response.context['page_obj'].object_list
        self.assertIsInstance(posts, List)

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

        page = self.PROFILE_FOLLOW
        client.get(page)
        self.assertTrue(get_object_or_404(Follow, user=user, author=author))

        page = self.FOLLOW_PAGE
        self.check_paginator(client, page)

        response = client.get(page)
        self.assertTemplateUsed(response, template)
        posts = response.context['page_obj'].object_list
        self.assertIsInstance(posts, List)

        authors = [
            follow.author
            for follow in Follow.objects.filter(user=user)
        ]
        posts_db = Post.objects.filter(author__in=authors)
        for post in posts:
            with self.subTest(post=post.pk):
                self.assertIn(post, posts_db)

        page = self.PROFILE_UNFOLLOW
        client.get(page)

    def test_group_list_page(self):
        """Тест страницы группы."""
        group = self.group
        client = self.client
        template = 'posts/group_list.html'

        page = self.GROUP_PAGE
        self.check_paginator(client, page, group=group)

        response = client.get(page)
        self.assertTemplateUsed(response, template)
        response_group = response.context.get('group')
        self.assertEqual(response_group, group)

        posts = response.context['page_obj'].object_list
        for post in posts:
            with self.subTest(post=post):
                self.assertEqual(post.group, group)
                self.assertIsInstance(post.image, ImageFieldFile)

    def test_profile_page(self):
        """Тест страницы профиля автора."""
        author = self.author
        client = self.client
        template = 'posts/profile_detail.html'

        page = self.PROFILE_PAGE
        self.check_paginator(client, page, author=author)

        response = client.get(page)
        self.assertTemplateUsed(response, template)
        response_author = response.context.get('author')
        self.assertEqual(response_author, author)

        posts = response.context['page_obj'].object_list
        for post in posts:
            with self.subTest(post=post):
                self.assertEqual(post.author, author)
                self.assertIsInstance(post.image, ImageFieldFile)

    def test_GET_post_detail_page(self):
        """Тест страницы выбранного поста GET-запрос."""
        post = self.post
        client = self.client
        template = 'posts/post_detail.html'

        page = self.POST_DETAIL_PAGE
        response = client.get(page)
        self.assertTemplateUsed(response, template)
        response_post = response.context.get('post')
        self.assertEqual(response_post, post)
        self.assertIsInstance(response_post.image, ImageFieldFile)

    def test_POST_post_comment_page_anon(self):
        """Тест написания комментария к посту Анонимом."""
        post = self.post
        page = self.POST_COMMENT

        new_comment_data = {'text': 'Новый комментарий'}

        for client in self.client, self.client_user:
            count_comments_bef = Comment.objects.filter(post=post).count()
            response = client.post(page, data=new_comment_data)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            count_comments_aft = Comment.objects.filter(post=post).count()
            if client == self.client:
                self.assertEqual(count_comments_bef, count_comments_aft)
            elif client == self.client_user:
                self.assertEqual(count_comments_bef, count_comments_aft - 1)

    def test_post_create_page(self):
        """Тест страницы создания нового поста."""
        user = self.author
        group = self.group
        client = self.client_author
        template = 'posts/create_post.html'

        page = self.POST_CREATE_PAGE

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
        self.assertEqual(count_posts_before, count_posts_after - 1)

        redirect_page = self.PROFILE_PAGE
        self.assertRedirects(response, redirect_page)

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

        page = self.POST_EDIT_PAGE
        response = client.get(page)
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
        self.assertEqual(count_posts_after, count_posts_before)

        redirect_page = self.POST_DETAIL_PAGE
        self.assertRedirects(response, redirect_page)

        self.assertTrue(
            get_object_or_404(
                Post,
                text=new_post_data.get('text'),
                group=new_post_data.get('group'),
                author=post.author,
            )
        )

    def test_post_delete_page(self):
        """Тест страницы удаления поста."""
        post = self.post
        page = self.POST_DELETE

        for client in self.client_user, self.client_author:
            client.get(page)
            posts = Post.objects.all()
            if client == self.client_user:
                self.assertIn(post, posts)
            elif client == self.client_author:
                self.assertNotIn(post, posts)
