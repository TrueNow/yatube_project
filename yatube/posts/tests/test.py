from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostsTestCase(TestCase):
    COUNT_USERS_TEST = 2
    COUNT_GROUPS_TEST = 2
    COUNT_POSTS_TEST = 19

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = User.objects.bulk_create(
            [
                User(
                    pk=i,
                    username=['Author', 'User'][i - 1]
                ) for i in range(1, cls.COUNT_USERS_TEST + 1)
            ]
        )
        cls.author = users[0]
        cls.user = users[1]

        groups = Group.objects.bulk_create(
            [
                Group(
                    pk=i,
                    title=f'Тестовая группа {i}',
                    slug=f'test_slug_{i}',
                    description=f'Тестовое описание {i}',
                ) for i in range(1, cls.COUNT_GROUPS_TEST + 1)
            ]
        )
        cls.group = groups[0]

        posts = Post.objects.bulk_create(
            [
                Post(
                    pk=i + 1,
                    author=cls.author,
                    text=f'Тестовый пост {i + 1}',
                    group=cls.group,
                ) for i in range(cls.COUNT_POSTS_TEST)
            ],
            batch_size=5,
        )
        cls.post = posts[cls.COUNT_POSTS_TEST - 1]

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
