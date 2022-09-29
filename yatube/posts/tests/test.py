from django.test import TestCase, Client
from django.urls import reverse_lazy

from posts import pages
from posts.models import Group, Post, User


class PostsTestCase(TestCase):
    COUNT_POSTS_TEST = 32

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        usernames = ('Author', 'User')
        User.objects.bulk_create(
            [
                User(
                    username=username
                ) for username in usernames
            ]
        )
        cls.author, cls.user = User.objects.all()

        groups = (1, 2)
        Group.objects.bulk_create(
            [
                Group(
                    title=f'Тестовая группа {group}',
                    slug=f'test_slug_{group}',
                    description=f'Тестовое описание {group}',
                ) for group in groups
            ]
        )
        cls.groups = Group.objects.all()
        cls.group = cls.groups[0]

        Post.objects.bulk_create(
            [
                Post(
                    author=cls.author,
                    text=f'Тестовый пост {i + 1}',
                    group=cls.groups[i % 2],
                ) for i in range(cls.COUNT_POSTS_TEST)
            ],
            batch_size=5,
        )
        cls.posts = Post.objects.all()
        cls.post = cls.posts[cls.COUNT_POSTS_TEST - 1]

        cls.INDEX_PAGE = reverse_lazy(pages.INDEX_PAGE)
        cls.FOLLOW_PAGE = reverse_lazy(pages.FOLLOW_PAGE)
        cls.GROUP_PAGE = reverse_lazy(pages.GROUP_PAGE,
                                      args=[cls.group.slug])
        cls.PROFILE_PAGE = reverse_lazy(pages.PROFILE_PAGE,
                                        args=[cls.author.username])
        cls.PROFILE_FOLLOW = reverse_lazy(pages.PROFILE_FOLLOW,
                                          args=[cls.author.username])
        cls.PROFILE_UNFOLLOW = reverse_lazy(pages.PROFILE_UNFOLLOW,
                                            args=[cls.author.username])
        cls.POST_CREATE_PAGE = reverse_lazy(pages.POST_CREATE_PAGE)
        cls.POST_DETAIL_PAGE = reverse_lazy(pages.POST_DETAIL_PAGE,
                                            args=[cls.post.pk])
        cls.POST_COMMENT = reverse_lazy(pages.POST_COMMENT,
                                        args=[cls.post.pk])
        cls.POST_EDIT_PAGE = reverse_lazy(pages.POST_EDIT_PAGE,
                                          args=[cls.post.pk])
        cls.POST_DELETE = reverse_lazy(pages.POST_DELETE,
                                       args=[cls.post.pk])

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
