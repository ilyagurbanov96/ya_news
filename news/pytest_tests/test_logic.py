from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_user_can_create_comment(author_client, author,
                                 form_data, news, url_detail):
    """Авторизованный пользователь может отправить комментарий."""
    comment_count = Comment.objects.count()
    response = author_client.post(url_detail, data=form_data)
    assertRedirects(response, f'{url_detail}#comments')
    assert Comment.objects.count() == comment_count + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_anonymous_user_cant_create_comment(client, form_data,
                                            url_detail, url_login):
    """Анонимный пользователь не может отправить комментарий."""
    comment_count = Comment.objects.count()
    response = client.post(url_detail, data=form_data)
    expected_url = f'{url_login}?next={url_detail}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comment_count


def test_author_can_edit_comment(author_client, form_data, url_edit,
                                 comment, news, author, url_detail_comment):
    """Автор может редактировать коментарий"""
    comment_count = Comment.objects.count()
    response = author_client.post(url_edit, form_data)
    assertRedirects(response, f'{url_detail_comment}#comments')
    new_comment = Comment.objects.get()
    assert Comment.objects.count() == comment_count
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == comment.news


def test_author_can_delete_comment(author_client, comment,
                                   url_detail_comment, url_delete):
    """Автор может удалять комунтарий."""
    comment_count = Comment.objects.count()
    response = author_client.post(url_delete)
    assertRedirects(response, f'{url_detail_comment}#comments')
    assert Comment.objects.count() == comment_count - 1


def test_not_author_cant_edit_comment(not_author_client, form_data,
                                      comment, author, url_edit, news):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    comment_count = Comment.objects.count()
    response = not_author_client.post(url_edit, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comment_count
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment_from_db.text == comment.text
    assert comment_from_db.author == author
    assert comment_from_db.news == comment.news


def test_not_author_cant_delete_comment(not_author_client,
                                        url_delete):
    """Авторизованный пользователь не может
    удалять чужие комментарии.
    """
    comment_count = Comment.objects.count()
    response = not_author_client.post(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comment_count


def test_user_cant_use_bad_words(author_client, url_detail):
    """Комментарий содержащий запрещённые слова, не будет опубликован.
    А форма вернёт ошибку.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comment_count = Comment.objects.count()
    response = author_client.post(url_detail, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == comment_count
