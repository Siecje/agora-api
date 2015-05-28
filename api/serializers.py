from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Comment, Page


class RelatedUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'url',)


class RelatedPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id',)


class PageSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Page
        fields = ('id', 'name', 'stylesheet', 'user', 'created', 'updated')


class CommentSerializer(serializers.ModelSerializer):
    user = RelatedUserSerializer()
    page = RelatedPageSerializer()

    class Meta:
        model = Comment
        fields = ('id', 'text', 'user', 'parent', 'page', 'created', 'updated')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('username', 'email')


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password')
