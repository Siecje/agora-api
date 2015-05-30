from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, list_route
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .models import Comment, Page, User
from .serializers import CommentSerializer, CreateCommentSerializer, \
                         PageSerializer, UserSerializer, CreateUserSerializer


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'pages': reverse('page-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format),
        'auth-token': reverse('auth-token', request=request, format=format)
    })


class PageViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    parser_classes = (MultiPartParser, FormParser, JSONParser,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Page.objects.all()
    serializer_class = PageSerializer

    def perform_create(self, serializer):
        if self.request.data.get('stylesheet'):
            serializer.save(stylesheet=self.request.data.get('stylesheet'), user=self.request.user)
        else:
            serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if self.request.data.get('stylesheet'):
            serializer.save(stylesheet=self.request.data.get('stylesheet'), user=self.request.user)
        else:
            serializer.save(user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = CommentSerializer

    def get_queryset(self, id):
        page = get_object_or_404(Page, pk=id)
        return Comment.objects.filter(page=page)

    def list(self, request, id):
        page = get_object_or_404(Page, pk=id)
        comments = page.comments.filter(parent=None)
        response = []
        for comment in comments:
            response.append(comment.to_JSON())
        return Response(response)

    def create(self, request, id):
        page = get_object_or_404(Page, pk=id)

        serialized = CreateCommentSerializer(data=request.data)
        if serialized.is_valid():
            comment = Comment.objects.create(
                page=page,
                user=request.user,
                text=serialized.validated_data.get('text'),
                parent=serialized.validated_data.get('parent'))
            return Response(CommentSerializer(
                comment,
                context={'request': request}).data,
                status=status.HTTP_201_CREATED)
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


class IsAdminOrOwner(permissions.BasePermission):
    """
    Object-level permission to allow admins or the user of an object to access it.
    Assumes the model instance has an `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        # Instance must have an attribute named `user`.
        return obj == request.user


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrOwner,)

    @list_route(methods=['POST'])
    def create_user(self, request):
        serialized = CreateUserSerializer(data=request.DATA)
        if serialized.is_valid():
            user = User.objects.create_user(
                serialized.validated_data.get('username'),
                serialized.validated_data.get('email'),
                serialized.validated_data.get('password'))

            return Response(UserSerializer(user).data,
                            status=status.HTTP_201_CREATED)
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        if self.request.user.is_anonymous():
            return User.objects.none()
        elif self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)
