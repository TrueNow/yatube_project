from .test import PostsTestCase


class PostsModelTest(PostsTestCase):
    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        models_verbose_dict = {
            self.post: 'Тестовый пост 15',
            self.group: 'Тестовая группа',
        }
        for model, verbose_name in models_verbose_dict.items():
            with self.subTest(model=model):
                self.assertEqual(
                    str(model),
                    verbose_name[:self.post.COUNT_CHARS]
                )

    def test_post_verbose_name(self):
        """Проверяем, что у моделей verbose_name совпадает с ожидаемым."""
        models_verbose_dict = {
            self.post: {
                'text': 'Текст поста',
                'pub_date': 'Дата публикации',
                'author': 'Автор',
                'group': 'Группа',
            },
            self.group: {
                'title': 'Название',
                'slug': 'Ссылка',
                'description': 'Описание',
            }
        }
        for model, fields_verbose_dict in models_verbose_dict.items():
            with self.subTest(model=model):
                for field, verbose_name in fields_verbose_dict.items():
                    with self.subTest(field=field):
                        self.assertEqual(
                            model._meta.get_field(field).verbose_name,
                            verbose_name
                        )

    def test_post_help_text(self):
        """Проверяем, что у моделей help_text совпадает с ожидаемым."""
        models_help_texts_dict = {
            self.post: {
                'text': 'Текст поста',
                'group': 'Группа, к которой относится пост',
            },
            self.group: {
                'slug': 'Будущая часть URL-адреса страницы группы',
            }
        }
        for model, fields_help_texts_dict in models_help_texts_dict.items():
            with self.subTest(model=model):
                for field, help_text in fields_help_texts_dict.items():
                    with self.subTest(field=field):
                        self.assertEqual(
                            model._meta.get_field(field).help_text,
                            help_text
                        )
