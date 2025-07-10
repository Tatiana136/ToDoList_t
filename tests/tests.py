from http import HTTPStatus
from rest_framework.test import APITestCase
from django.urls import reverse
from api.models import User, Category, TodoList


class TestRoutes(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author', password='qwerty55')
        cls.user = User.objects.create(username='User5', password='user55', email='User5@mail.ru')
        cls.category = Category.objects.create(name='Отпуск')
        cls.todo = TodoList.objects.create(
            title='Мальдивы',
            content='Снять домик',
            author=cls.author,
            category=cls.category
        )
    
    def test_author_can_edit_and_delete(self):
        """Редактирование и удаление заметки."""

        self.client.force_authenticate(user=self.author)
        url = reverse('todolist-detail', args=[self.todo.id])
        response = self.client.patch(url, data={'title': 'Турция'}, format='json')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Турция')

        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        exists = TodoList.objects.filter(id=self.todo.id).exists()
        self.assertFalse(exists)

    def test_other_cannot_edit_or_delete(self):
        """Авторизированный пользователь не может редактировать чужую заметку."""

        self.client.force_authenticate(user=self.user)
        url = reverse('todolist-detail', args=[self.todo.id])
        response = self.client.patch(url, data={'title': 'Стороннее обновление'}, format='json')
        self.assertIn(response.status_code, (HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND))
        response = self.client.delete(url)
        self.assertIn(response.status_code, (HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND))
