import os
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from api.models import Page, User


class PageTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='one', email='one@example.com', password='one')

        token = Token.objects.get(user__username=self.user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_create_page_endpoint(self):
        url = reverse('page-list')

        data = {
            'name': 'Endpoint Works',
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Endpoint Works')

    def _create_test_file(self, path):
        f = open(path, 'w')
        f.write('.title { font-size: 1.5rem }\n')
        f.close()
        f = open(path, 'rb')
        return f

    def test_add_page_stylesheet(self):
        page = Page.objects.create(name='First', user=self.user)
        url = reverse('page-detail', kwargs={'id': page.id})

        stylesheet = self._create_test_file(os.path.join('stylesheets', 'stylesheet.css'))

        response = self.client.patch(url, data={'stylesheet': stylesheet}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stylesheet'], '/static/' + response.data['id'] + '.css')

    def test_create_page_with_stylesheet(self):
        url = reverse('page-list')

        stylesheet = self._create_test_file(os.path.join('stylesheets', 'stylesheet.css'))

        data = {
            'name': 'Created',
            'stylesheet': stylesheet
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Created')
        self.assertEqual(response.data['stylesheet'], '/static/' + response.data['id'] + '.css')

    def test_add_comment_to_page(self):
        page = Page.objects.create(name='First', user=self.user)
        url = reverse('page-comments', kwargs={'id': page.id})

        response = self.client.post(url, data={'text': 'comment'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment_with_parent_to_page(self):
        page = Page.objects.create(name='First', user=self.user)
        url = reverse('page-comments', kwargs={'id': page.id})

        # First comment
        response = self.client.post(url, data={'text': 'comment'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        parent = response.data.get('id')

        response = self.client.post(url, data={'text': 'comment', 'parent': parent})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
