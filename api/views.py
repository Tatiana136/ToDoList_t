from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import TodoList, Category, User
from .serializers import TodoListSerializer, CategorySerializer, UserSerializer, PasswordSerializer
from api.permissions import IsAdminOrAuthorOrReadOnly
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import IntegrityError
import logging


logger = logging.getLogger('api')


class CustomUserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminOrAuthorOrReadOnly]
        # Создаем и возвращаем список объектов(экземпляров) пермишенов, вызывая констрктор каждого класса
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        # на соответствие требованиям базы
        except IntegrityError as e:
            logger.error(f"Ошибка при создании пользователя: {e}")
            return Response(
                {'ERROR': 'Ошибка целостности данных. Проверьте уникальность.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при создании пользователя: {e}")
            return Response(
                {'ERROR': 'Произошла ошибка. Попробуйте еще раз.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Изменение данных пользователя."""
        if request.method == 'GET':
            return Response(
                self.get_serializer(request.user).data,
                status=status.HTTP_200_OK
            )
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # Ставим detail=False, чтобы метод не требовал id
    @action(
        detail=False,
        methods=['POST'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        user = request.user
        serializer = PasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TodoViewSet(viewsets.ModelViewSet):
    """Вьюсет для задач."""
    queryset = TodoList.objects.all()
    serializer_class = TodoListSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminOrAuthorOrReadOnly]
        # Создаем и возвращаем список объектов(экземпляров) пермишенов, вызывая конструктор каждого класса
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        category_name = self.request.data.get('category')
        category_obj = get_object_or_404(Category, pk=category_name)
        serializer.save(author=self.request.user, category=category_obj)
    
    @action(detail=True, methods=['get'], url_path='api/todo-detail')
    def todo_detail_api(self, request, pk=None):
        todo = get_object_or_404(TodoList, pk=pk)
        categories = Category.objects.all()
        return Response({
            'todo': TodoListSerializer(todo).data,
            'categories': CategorySerializer(categories, many=True).data
        })

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        checked_ids = request.data.get('checked_ids', [])
        TodoList.objects.filter(id__in=checked_ids).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
  
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def share_access(self, request, pk=None):
        todo = get_object_or_404(TodoList, pk=pk)

        if request.user != todo.author and not request.user.is_staff:
            return Response({'detail': 'Нет прав для изменения доступа.'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        grant = request.data.get('grant')

        if user_id is None or grant is None:
            return Response({'detail': 'Требуются поля: user_id и grant.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, pk=user_id)

        if grant:
            todo.shared_with.add(user)
            message = f'Пользователю {user.username} предоставлен доступ.'
        else:
            todo.shared_with.remove(user)
            message = f'У пользователя {user.username} отозван доступ.'
        return Response({'detail': message}, status=status.HTTP_200_OK)
