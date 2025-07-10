ЭНДПОИНТЫ:

1) Регистрация пользователя:
POST: http://127.0.0.1:8000/api/auth/users/

{
  "username": "user2",
  "email": "user2@mail.ru",
  "password": "qwerty2!"
}

2) Вход:
POST: http://127.0.0.1:8000/api/auth/token/login/

{
  "email": "user2@mail.ru",
  "password": "qwerty2!"
}

3) Получить данные своего пользователя: 
GET: http://127.0.0.1:8000/api/auth/users/me/
Headers:
Authorization: Value: Token мой токен

4) Создать категорию:  
POST: http://127.0.0.1:8000/api/categories/
Headers:
Authorization: Value: Token мой токен
Body:

{
  "name": "Домашнее"
}

5) Создать задачу:
POST: http://127.0.0.1:8000/api/todos/
Headers:
Authorization: Value: Token мой токен
Body:
{
  "title": "Продукты",
  "due_date": "2025-07-08",
  "content": "Купить хлеб и молоко",
  "category": 1
}

6) Просмотреть список задач:
GET: http://127.0.0.1:8000/api/todos/

7) Просмотреть конкретную задачу:
GET: http://127.0.0.1:8000/api/todos/{id}/

8) Обновить частично задачу:
PATCH: http://127.0.0.1:8000/api/todos/{id}/
Headers:
Authorization: Value: Token мой токен
Body:
{
  "title": "Продукты 2(обновлено-2)"
}

9) Обновить полностью задачу:
PUT: http://127.0.0.1:8000/api/todos/{id}/
Headers:
Authorization: Value: Token мой токен
Body:
{
  "title": "Продукты 2(обновлено-3)",
  "due_date": "2025-07-08",
  "content": "Купить хлеб и молоко, и еще морковку и МАСЛО!!",
  "category": 1
}

10) Удалить задачу:
DELETE: http://127.0.0.1:8000/api/todos/{id}/
Headers:
Authorization: Value: Token мой токен

11) Выдача/отнятие прав на задачу другому пользователю:
POST: http://127.0.0.1:8000/api/todos/{id задачи}/share_access/
Headers:
Authorization: Value: Token мой токен
Body:

{
  "user_id": 2,
  "grant": true
}
