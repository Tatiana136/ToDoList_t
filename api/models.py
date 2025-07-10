from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

MAX = 150


class UserRole:
    """Модель пользователя."""

    USER = 'user'
    ADMIN = 'admin'

    CHOICES = [
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    ]


class User(AbstractUser):
    """Кастомизированная модель пользователя."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,)
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=MAX,
        blank=True,
        unique=True)
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX,
        blank=True,)
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX,
        blank=True,)
    role = models.CharField(
        verbose_name='Роль',
        max_length=20,
        choices=UserRole.CHOICES,
        default=UserRole.USER,)
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def admin(self):
        return self.role == UserRole.ADMIN

    def __str__(self):
        return self.email


class Category(models.Model):
    """Создаем таблицу категорий. Поля: id, name."""
    name = models.CharField(max_length=128, unique=True)
    class Meta:
        verbose_name = ("Category")
        verbose_name_plural = ("Categories")
    
    def __str__(self):
        return self.name


class TodoList(models.Model):
    title = models.CharField(max_length=128)
    content = models.TextField(blank=True)
    image = models.ImageField('Фото', upload_to='images', blank=True)
    created = models.DateField(default=timezone.now)
    # Конечная дата. Дедлайн.
    due_date = models.DateField(default=timezone.now)
    # Запрещает удалять категорию, в которой есть заметки.
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='todos')
    # Поле хранит связь с пользователями, которым предоставлен доступ к задаче
    shared_with = models.ManyToManyField(User, related_name='shared_todos', blank=True)
    class Meta:
        ordering = ["-created"]
    def __str__(self):
        return self.title
