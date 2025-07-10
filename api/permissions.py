from rest_framework import permissions


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    """Права:
    - Администратор все
    - Автор заметки, изменение и удаление своих заметок
    - Остальные только чтение
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # getattr — функция возвращает значение атрибута объекта (admin - имя атрибута, который хотим получить)
        # Если у пользователя есть атрибут admin (например, булево поле в модели User или is_admin), 
        # то getattr вернёт его значение (True или False).
        # Если атрибута нет (например, в стандартной модели User его нет), то getattr вернёт False,
        # чтобы не получить ошибку AttributeError.
        if request.user.is_authenticated and getattr(request.user, 'admin', False):
            return True
        # Разрешить изменение и удаление только автору
        return obj.author == request.user
