from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db

HOME = pytest.lazy_fixture('url_home')
DETAIL = pytest.lazy_fixture('url_detail')
LOGIN = pytest.lazy_fixture('url_login')
LOGOUT = pytest.lazy_fixture('url_logout')
SIGNUP = pytest.lazy_fixture('url_signup')
EDIT = pytest.lazy_fixture('url_edit')
DELETE = pytest.lazy_fixture('url_delete')
ANONIM = pytest.lazy_fixture('client')
NOT_AUTHOR = pytest.lazy_fixture('not_author_client')
AUTHOR = pytest.lazy_fixture('author_client')


@pytest.mark.parametrize(
    'name, parametrized_client, expected_status',
    (
        (HOME, ANONIM, HTTPStatus.OK),
        (DETAIL, ANONIM, HTTPStatus.OK),
        (LOGIN, ANONIM, HTTPStatus.OK),
        (LOGOUT, ANONIM, HTTPStatus.OK),
        (SIGNUP, ANONIM, HTTPStatus.OK),
        (EDIT, AUTHOR, HTTPStatus.OK),
        (DELETE, AUTHOR, HTTPStatus.OK),
        (EDIT, NOT_AUTHOR, HTTPStatus.NOT_FOUND),
        (DELETE, NOT_AUTHOR, HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_availability_for_anonymous_user(parametrized_client, name,
                                               expected_status):
    """Доступность урлов анонимному пользователю."""
    response = parametrized_client.get(name)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, redirect',
    (
        (EDIT, LOGIN),
        (DELETE, LOGIN),
    ),
)
def test_redirects(client, name, redirect):
    """Редирект анонимного пользователя."""
    expected_url = f'{redirect}?next={name}'
    response = client.get(name)
    assertRedirects(response, expected_url)
