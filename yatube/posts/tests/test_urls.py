from http import HTTPStatus

from .test import PostsTestCase


class PostsURLTests(PostsTestCase):
    def test_url_status_code(self):
        """Проверка status_code страниц."""
        clients_urls_dict = {
            self.client_anonymous: {
                '/': HTTPStatus.OK,
                f'/group/{self.group.slug}/': HTTPStatus.OK,
                f'/profile/{self.author.username}/': HTTPStatus.OK,
                f'/posts/{self.post.pk}/': HTTPStatus.OK,
                '/create/': HTTPStatus.FOUND,
                f'/posts/{self.post.pk}/edit/': HTTPStatus.FOUND,
                '/unexisting_page/': HTTPStatus.NOT_FOUND,
            },
            self.client_author: {
                f'/posts/{self.post.pk}/edit/': HTTPStatus.OK,
            },
            self.client_user: {
                '/create/': HTTPStatus.OK,
                f'/posts/{self.post.pk}/edit/': HTTPStatus.FOUND,
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
            self.client_anonymous: {
                '/create/': (
                    '/auth/login/?next=/create/'
                ),
                f'/posts/{self.post.pk}/edit/': (
                    f'/auth/login/?next=/posts/{self.post.pk}/edit/'
                ),
            },
            self.client_user: {
                f'/posts/{self.post.pk}/edit/': (
                    f'/posts/{self.post.pk}/'
                ),
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
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.author.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for url, template in urls_templates_dict.items():
            with self.subTest(address=url):
                response = self.client_author.get(url)
                self.assertTemplateUsed(response, template)
