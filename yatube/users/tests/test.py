from django.contrib.auth import get_user_model
from django.test import TestCase, Client


User = get_user_model()


class PostsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.user = User.objects.create_user(username='User')

    def setUp(self):
        # Создаем неавторизованный клиент
        self.client_anonymous = Client()
        self.client_anonymous.name = 'Anonymous'

        # Создаем авторизованный клиент (автор)
        self.client_author = Client()
        self.client_author.force_login(self.author)
        self.client_author.name = self.author.username

        # Создаем авторизованный клиент (не автор)
        self.client_user = Client()
        self.client_user.force_login(self.user)
        self.client_user.name = self.user.username
