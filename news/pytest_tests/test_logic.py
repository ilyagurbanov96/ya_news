from pytest_django.asserts import assertRedirects
from http import HTTPStatus
from django.urls import reverse
import pytest
from news.models import Comment


def test_user_can_create_comment(author_client, author,
                                 form_data, pk_for_args):
    url = reverse('news:detail', args=pk_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, pk_for_args):
    url = reverse('news:detail', args=pk_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, form_data,
                                 comment, pk_for_args):
    url = reverse('news:detail', args=pk_for_args)
    url_edit = reverse('news:edit', args=pk_for_args)
    response = author_client.post(url_edit, form_data)
    assertRedirects(response, f'{url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_author_can_delete_comment(author_client, pk_for_args):
    url = reverse('news:detail', args=pk_for_args)
    url_delete = reverse('news:delete', args=pk_for_args)
    response = author_client.post(url_delete)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 0


def test_not_author_cant_edit_comment(not_author_client, form_data,
                                      comment, pk_for_args):
    url_edit = reverse('news:edit', args=pk_for_args)
    response = not_author_client.post(url_edit, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_not_author_cant_delete_comment(not_author_client, pk_for_args):
    url_delete = reverse('news:delete', args=pk_for_args)
    response = not_author_client.post(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
