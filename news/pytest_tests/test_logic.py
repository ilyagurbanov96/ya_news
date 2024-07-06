from pytest_django.asserts import assertRedirects, assertFormError
from http import HTTPStatus
from django.urls import reverse
import pytest
from news.models import Comment
from news.forms import BAD_WORDS, WARNING


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
                                 comment):
    url = reverse('news:detail', args=(comment.id,))
    url_edit = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url_edit, form_data)
    assertRedirects(response, f'{url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:detail', args=(comment.id,))
    url_delete = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url_delete)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 0


def test_not_author_cant_edit_comment(not_author_client, form_data,
                                      comment):
    url_edit = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url_edit, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_not_author_cant_delete_comment(not_author_client, comment):
    url_delete = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=(WARNING))
    comments_count = Comment.objects.count()
    assert comments_count == 0
