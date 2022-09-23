from http import HTTPStatus

from .test import *


class PostsURLTests(PostsTestCase):
    def test_url_status_code(self):
        """Проверка status_code страниц."""
        clients_urls_dict = {
            self.client: {
                INDEX_PAGE: HTTPStatus.OK,
                FOLLOW_PAGE: HTTPStatus.FOUND,
                GROUP_PAGE(self.group.slug): HTTPStatus.OK,
                PROFILE_PAGE(self.author.username): HTTPStatus.OK,
                POST_DETAIL_PAGE(self.post.pk): HTTPStatus.OK,
                POST_CREATE_PAGE: HTTPStatus.FOUND,
                POST_EDIT_PAGE(self.post.pk): HTTPStatus.FOUND,
                PROFILE_FOLLOW(self.author.username): HTTPStatus.FOUND,
                PROFILE_UNFOLLOW(self.author.username): HTTPStatus.FOUND,
                UNEXISTING_PAGE: HTTPStatus.NOT_FOUND,
            },
            self.client_author: {
                FOLLOW_PAGE: HTTPStatus.OK,
                POST_EDIT_PAGE(self.post.pk): HTTPStatus.OK,
            },
            self.client_user: {
                POST_CREATE_PAGE: HTTPStatus.OK,
                POST_EDIT_PAGE(self.post.pk): HTTPStatus.FOUND,
                PROFILE_FOLLOW(self.author.username): HTTPStatus.FOUND,
                PROFILE_UNFOLLOW(self.author.username): HTTPStatus.FOUND,
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
                POST_CREATE_PAGE: (
                    f'/auth/login/?next={POST_CREATE_PAGE}'
                ),
                POST_EDIT_PAGE(self.post.pk): (
                    f'/auth/login/?next={POST_EDIT_PAGE(self.post.pk)}'
                ),
            },
            self.client_user: {
                POST_EDIT_PAGE(self.post.pk): (
                    f'{POST_DETAIL_PAGE(self.post.pk)}'
                )
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
        urls_templates_dict = {
            INDEX_PAGE: 'posts/index.html',
            FOLLOW_PAGE: 'posts/index.html',
            GROUP_PAGE(self.group.slug): 'posts/group_detail.html',
            PROFILE_PAGE(self.author.username): 'posts/profile_detail.html',
            POST_DETAIL_PAGE(self.post.pk): 'posts/post_detail.html',
            POST_CREATE_PAGE: 'posts/create_post.html',
            POST_EDIT_PAGE(self.post.pk): 'posts/create_post.html',
        }
        for url, template in urls_templates_dict.items():
            with self.subTest(address=url):
                response = self.client_author.get(url)
                self.assertTemplateUsed(response, template)
