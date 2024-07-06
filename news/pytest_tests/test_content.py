from django.conf import settings
from django.urls import reverse
import pytest
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, all_news, comment):
    detail_url = reverse('news:detail', args=(comment.id,))
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, comment):
    detail_url = reverse('news:detail', args=(comment.id,))
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(client, author, comment):
    detail_url = reverse('news:detail', args=(comment.id,))
    client.force_login(author)
    response = client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
