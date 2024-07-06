import pytest
from news.models import News, Comment
from django.test.client import Client
from django.conf import settings
from datetime import datetime, timedelta


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
    return all_news


@pytest.fixture
def pk_for_args(news):
    return (news.pk,)


@pytest.fixture
def form_data():
    return {
        'text': 'BAD_WORDS[0]',
        'author': 'author'
    }
