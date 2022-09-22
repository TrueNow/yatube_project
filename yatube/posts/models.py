from django.db import models
from django.contrib.auth import get_user_model
from django.shortcuts import reverse


User = get_user_model()
COUNT_CHARS: int = 15


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Ссылка',
        help_text='Будущая часть URL-адреса страницы группы',
    )
    description = models.TextField(
        verbose_name='Описание',
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse(
            'posts:group_list',
            kwargs={'slug': self.slug}
        )


class Post(models.Model):
    C_CHARS_SHORT_TEXT = 100

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой относится пост'
    )
    image = models.ImageField(
        blank=True,
        upload_to='posts/',
        verbose_name='Картинка'
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.text[:COUNT_CHARS]}'

    def get_absolute_url(self):
        return reverse(
            'posts:post_detail',
            kwargs={'post_id': self.pk}
        )

    def short_text(self):
        if len(str(self.text)) <= self.C_CHARS_SHORT_TEXT:
            return self.text
        return f'{self.text[:self.C_CHARS_SHORT_TEXT]}...'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Комментарий',
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created',)

    def __str__(self):
        return self.text[:COUNT_CHARS]

    def get_absolute_url(self):
        return reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        )


class Follow(models.Model):
    DoesNotExist = None
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
