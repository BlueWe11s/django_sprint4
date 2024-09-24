from django.db import models
from django.contrib.auth import get_user_model

from core.models import PublishedModel
from .querysets import PostsQuerySet

MAX_LENGTH = 256

User = get_user_model()


class Category(PublishedModel):
    title = models.CharField(
        max_length=MAX_LENGTH, blank=False, verbose_name="Заголовок"
    )
    description = models.TextField(blank=False, verbose_name="Описание")
    slug = models.SlugField(
        unique=True,
        blank=False,
        help_text="Идентификатор страницы для URL; "
        "разрешены символы латиницы, цифры, дефис и подчёркивание.",
        verbose_name="Идентификатор",
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"
        indexes = [
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField(
        max_length=MAX_LENGTH, blank=False, verbose_name="Название места"
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class Post(PublishedModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
        related_name="profile"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Местоположение",
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
    )

    title = models.CharField(max_length=MAX_LENGTH, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text="Если установить дату и время "
        "в будущем — можно делать отложенные публикации.",
    )
    image = models.ImageField("Фото", blank=True)
    objects = PostsQuerySet.as_manager()

    class Meta:
        default_related_name = "posts"
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"

    def __str__(self):
        return self.title


class Comment(PublishedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="публикация",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор комментария"
    )
    text = models.TextField("Текст комментария")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at",]

    def __str__(self):
        return f"Комментарий пользователя {self.author}"
