import re
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from api.models import User, TodoList, Category


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label='Email')
    password = serializers.CharField(
        label='password',
        trim_whitespace=False
    )

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user:
                raise serializers.ValidationError(
                    'Невозможно войти в систему с предоставленными данными.'
                )
        else:
            raise serializers.ValidationError('Должны быть email и пароль.')
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'password',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_username(self, value):
        user = self.instance
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                'Неверный формат имени пользователя.'
            )
        qs = User.objects.filter(username=value)
        if user:
            qs = qs.exclude(pk=user.pk)
        if qs.exists():
            raise serializers.ValidationError(
                'Это имя пользователя уже занято.'
            )
        return value

    def validate_email(self, value):
        user = self.instance
        qs = User.objects.filter(email=value)
        if user:
            qs = qs.exclude(pk=user.pk)
        if qs.exists():
            raise serializers.ValidationError(
                'Этот адрес электронной почты уже занят.'
            )
        return value

    def create(self, validated_data):
        print("Создание пользователя с данными:", validated_data)
        # Пароль не должен храниться в обычном виде.
        # Поэтому сначала извлекаем пароль из validated_data
        # и удаляем его из словаря, потом передаем данные без пароля.
        password = validated_data.pop('password')
        user = super().create(validated_data)
        # Устанавливаем пароль с помощью метода set_password,
        # который преобразует его в хеш.
        user.set_password(password)
        user.save()
        return user


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.avatar:
            request = self.context.get('request')
            if request is not None:
                representation['avatar'] = request.build_absolute_uri(instance.avatar.url)
            else:
                representation['avatar'] = instance.avatar.url
        else:
            representation['avatar'] = None
        return representation


class PasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Текущий пароль неверный.')
        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                'Новый пароль должен содержать не менее 8 символов.'
            )
        return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TodoListSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    due_date = serializers.DateField()
    class Meta:
        model = TodoList
        fields = ['id', 'title', 'due_date', 'category', 'content', 'image']
