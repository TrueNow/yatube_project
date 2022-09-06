from http import HTTPStatus
from django.test import TestCase, Client


class AboutURLTests(TestCase):

    def setUp(self):
        self.anonymous_client = Client()

    def test_url_exists_at_desired_location(self):
        """Проверка status_code страниц для анонимного пользователя."""
        urls_codes_templates = (
            ('/about/author/', HTTPStatus.OK, 'about/author.html'),
            ('/about/tech/', HTTPStatus.OK, 'about/tech.html'),
        )
        for urls, status_code, template in urls_codes_templates:
            with self.subTest(address=urls):
                response = self.anonymous_client.get(urls)
                self.assertEqual(response.status_code, status_code)
                self.assertTemplateUsed(response, template)
