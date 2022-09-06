from http import HTTPStatus

from .test import PostsTestCase


class UsersURLTests(PostsTestCase):
    def test_url_status_code(self):
        """Проверка status_code страниц."""
        clients_urls_dict = {
            self.client_anonymous: {
                '/auth/signup/': HTTPStatus.OK,
                '/auth/login/': HTTPStatus.OK,
                '/auth/password_change/': HTTPStatus.FOUND,
                '/auth/password_change/done/': HTTPStatus.FOUND,
                '/auth/password_reset/': HTTPStatus.OK,
                '/auth/password_reset/done/': HTTPStatus.OK,
                '/auth/reset/done/': HTTPStatus.OK,
                '/auth/logout/': HTTPStatus.OK,
                '/auth/unexisting_page/': HTTPStatus.NOT_FOUND,
            },
            self.client_author: {
                '/auth/login/': HTTPStatus.OK,
                '/auth/password_change/': HTTPStatus.OK,
                '/auth/password_change/done/': HTTPStatus.OK,
                '/auth/reset/done/': HTTPStatus.OK,
                '/auth/logout/': HTTPStatus.OK,
            },
            self.client_user: {
            }
        }
        for client, urls_status_codes_dict in clients_urls_dict.items():
            with self.subTest(client=client.name):
                for url, status_code in urls_status_codes_dict.items():
                    with self.subTest(address=url):
                        response = client.get(url)
                        self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        urls_templates_dict = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logout.html',
        }
        for url, template in urls_templates_dict.items():
            with self.subTest(address=url):
                response = self.client_author.get(url)
                self.assertTemplateUsed(response, template)
