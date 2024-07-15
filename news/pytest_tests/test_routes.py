from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db

HOME = 'news:home'
DETAIL = 'news:detail'
LOGIN = 'users:login'
LOGOUT = 'users:logout'
SIGNUP = 'users:signup'
EDIT = 'news:edit'
DELETE = 'news:delete'


@pytest.mark.parametrize(
    'name, object, parametrized_client, expected_status',
    (
        (HOME, None,
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (DETAIL, pytest.lazy_fixture('news'),
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (LOGIN, None,
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (LOGOUT, None,
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (SIGNUP, None,
         pytest.lazy_fixture('client'), HTTPStatus.OK),
        (EDIT, pytest.lazy_fixture('comment'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (DELETE, pytest.lazy_fixture('comment'),
         pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (EDIT, pytest.lazy_fixture('comment'),
         pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (DELETE, pytest.lazy_fixture('comment'),
         pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_availability_for_anonymous_user(parametrized_client, name,
                                               expected_status, object):
    """Доступность урлов анонимному пользователю"""
    if object is not None:
        url = reverse(name, args=(object.id,))
    else:
        url = reverse(name)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, redirect',
    (
        (EDIT, LOGIN),
        (DELETE, LOGIN),
    ),
)
def test_redirects(client, name, comment, redirect):
    """Редирект анонимного пользователя."""
    login_url = reverse(redirect)
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
