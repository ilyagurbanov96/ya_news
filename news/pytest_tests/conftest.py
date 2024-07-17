from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news(author):
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def comment(author):
    comment = Comment.objects.create(
        news=News.objects.create(
            title='Заголовок',
            text='Текст заметки',
        ),
        author=author,
        text='Текст',
    )
    return comment


@pytest.fixture
def all_news():
    today = datetime.today()
    News.objects.bulk_create(
        News(title=f'Новость {index}', text='Просто текст.',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comments(news, author):
    today = datetime.today()
    Comment.objects.bulk_create(
        Comment(news=news, text=f'Комментарий {index}', author=author,
                created=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def form_data():
    return {
        'text': 'Коментарий',
    }


@pytest.fixture
def url_home():
    return reverse('news:home')


@pytest.fixture
def url_detail(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_detail_comment(comment):
    return reverse('news:detail', args=(comment.id,))


@pytest.fixture
def url_delete(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def url_edit(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def url_login():
    return reverse('users:login')


@pytest.fixture
def url_logout():
    return reverse('users:logout')


@pytest.fixture
def url_signup():
    return reverse('users:signup')
