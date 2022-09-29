from django.core.cache import cache
from http import HTTPStatus

from .test import PostsTestCase


class PostsURLTests(PostsTestCase):
    def test_url_status_code(self):
        """Проверка status_code страниц."""
        clients_urls_dict = {
            self.client: {
                self.INDEX_PAGE: HTTPStatus.OK,
                self.FOLLOW_PAGE: HTTPStatus.FOUND,
                self.GROUP_PAGE: HTTPStatus.OK,
                self.PROFILE_PAGE: HTTPStatus.OK,
                self.PROFILE_FOLLOW: HTTPStatus.FOUND,
                self.PROFILE_UNFOLLOW: HTTPStatus.FOUND,
                self.POST_CREATE_PAGE: HTTPStatus.FOUND,
                self.POST_DETAIL_PAGE: HTTPStatus.OK,
                self.POST_COMMENT: HTTPStatus.FOUND,
                self.POST_EDIT_PAGE: HTTPStatus.FOUND,
                self.POST_DELETE: HTTPStatus.FOUND,
                '/UNEXISTING_PAGE/': HTTPStatus.NOT_FOUND,
            },
            self.client_author: {
                self.FOLLOW_PAGE: HTTPStatus.OK,
                self.POST_EDIT_PAGE: HTTPStatus.OK,
            },
            self.client_user: {
                self.POST_CREATE_PAGE: HTTPStatus.OK,
                self.POST_EDIT_PAGE: HTTPStatus.FOUND,
                self.PROFILE_FOLLOW: HTTPStatus.FOUND,
                self.PROFILE_UNFOLLOW: HTTPStatus.FOUND,
            }
        }
        for client, urls_status_codes_dict in clients_urls_dict.items():
            with self.subTest(client=client.name):
                for url, status_code in urls_status_codes_dict.items():
                    with self.subTest(address=url):
                        response = client.get(url)
                        self.assertEqual(response.status_code, status_code)

    def test_urls_correct_redirect(self):
        """Перенаправление пользователей на соответствующие страницы."""
        clients_urls_dict = {
            self.client: {
                self.POST_COMMENT: (
                    f'/auth/login/?next={self.POST_COMMENT}'
                ),
                self.POST_CREATE_PAGE: (
                    f'/auth/login/?next={self.POST_CREATE_PAGE}'
                ),
                self.POST_EDIT_PAGE: (
                    f'/auth/login/?next={self.POST_EDIT_PAGE}'
                ),
                self.POST_DELETE: (
                    f'/auth/login/?next={self.POST_DELETE}'
                ),
            },
            self.client_user: {
                self.POST_EDIT_PAGE: f'{self.POST_DETAIL_PAGE}'
            },
        }
        for client, urls_redirects_dict in clients_urls_dict.items():
            with self.subTest(client=client.name):
                for url, redirect_url in urls_redirects_dict.items():
                    with self.subTest(address=url):
                        response = client.get(url, follow=True)
                        self.assertRedirects(response, redirect_url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        urls_templates_dict = {
            self.INDEX_PAGE: 'posts/index.html',
            self.FOLLOW_PAGE: 'posts/index.html',
            self.GROUP_PAGE: 'posts/group_list.html',
            self.PROFILE_PAGE: 'posts/profile_detail.html',
            self.POST_DETAIL_PAGE: 'posts/post_detail.html',
            self.POST_CREATE_PAGE: 'posts/create_post.html',
            self.POST_EDIT_PAGE: 'posts/create_post.html',
        }
        for url, template in urls_templates_dict.items():
            with self.subTest(address=url):
                response = self.client_author.get(url)
                self.assertTemplateUsed(response, template)
