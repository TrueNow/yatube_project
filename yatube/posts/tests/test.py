from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

INDEX_PAGE = reverse('posts:index')
FOLLOW_PAGE = reverse('posts:follow')
GROUP_PAGE = lambda group_slug: reverse(
    'posts:group_detail',
    args=[group_slug]
)
PROFILE_PAGE = lambda username: reverse(
    'posts:profile_detail',
    args=[username]
)
PROFILE_FOLLOW = lambda username: reverse(
    'posts:profile_follow',
    args=[username]
)
PROFILE_UNFOLLOW = lambda username: reverse(
    'posts:profile_unfollow',
    args=[username]
)
POST_DETAIL_PAGE = lambda post_id: reverse(
    'posts:post_detail',
    args=[post_id]
)
POST_CREATE_PAGE = reverse('posts:post_create')
POST_EDIT_PAGE = lambda post_id: reverse(
    'posts:post_edit',
    args=[post_id]
)
POST_DELETE_PAGE = lambda post_id: reverse(
    'posts:post_delete',
    args=[post_id]
)
UNEXISTING_PAGE = '/unexisting_page/'


class PostsTestCase(TestCase):
    COUNT_USERS_TEST = 2
    COUNT_GROUPS_TEST = 2
    COUNT_POSTS_TEST = 19

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        usernames = ['Author', 'User']
        User.objects.bulk_create(
            [
                User(username=usernames[i])
                for i in range(cls.COUNT_USERS_TEST)
            ]
        )
        cls.author, cls.user = User.objects.all()
        Group.objects.bulk_create(
            [
                Group(
                    title=f'Тестовая группа {i}',
                    slug=f'test_slug_{i}',
                    description=f'Тестовое описание {i}',
                ) for i in range(1, cls.COUNT_GROUPS_TEST + 1)
            ]
        )
        cls.group = Group.objects.get(pk=1)

        Post.objects.bulk_create(
            [
                Post(
                    author=cls.author,
                    text=f'Тестовый пост {i + 1}',
                    group=cls.group,
                ) for i in range(cls.COUNT_POSTS_TEST)
            ],
            batch_size=5,
        )
        cls.post = Post.objects.get(pk=cls.COUNT_POSTS_TEST)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.client = Client()
        self.client.name = 'Anonymous'

        # Создаем авторизованный клиент (автор)
        self.client_author = Client()
        self.client_author.force_login(self.author)
        self.client_author.name = self.author.username

        # Создаем авторизованный клиент (не автор)
        self.client_user = Client()
        self.client_user.force_login(self.user)
        self.client_user.name = self.user.username

    @staticmethod
    def create_page(name, kwargs):
        return reverse(name, kwargs=kwargs)
