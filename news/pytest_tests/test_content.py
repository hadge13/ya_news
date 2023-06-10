from django.urls import reverse
from django.conf import settings
from datetime import datetime, timedelta 
from django.utils import timezone
import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects
from news.models import News


#Количество новостей на главной странице — не более 10.
HOME_URL = reverse('news:home')

@pytest.mark.django_db
def test_news_count(eleven_news_on_page, client):
    # Загружаем главную страницу.
    response = client.get(HOME_URL)
    # Получаем список объектов из словаря контекста.
    news_list = response.context['news_list']
    # Определяем длину списка.
    news_count = len(news_list)
    # Проверяем, что на странице именно 10 новостей.
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

 # п.2 Новости отсортированы от самой свежей к самой старой. 
 # Свежие новости в начале списка.
@pytest.mark.django_db
def test_news_order(eleven_news_on_page, client):
    response =client.get(HOME_URL)
    news_list = response.context['news_list']
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in news_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)   # реверс - тру - переворачивает список
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates

#п. 3  Комментарии на странице отдельной новости отсортированы 
# от старых к новым: старые в начале списка, новые — в конце. 
@pytest.mark.django_db
def test_comments_order(comments_for_time, client, id_for_detail):
    url = reverse('news:detail', args=id_for_detail)
    response = client.get(url)
    # Проверяем, что объект новости находится в словаре контекста
    # под ожидаемым именем - названием модели.
    assert 'news' in response.context
    # Получаем объект новости.
    news = response.context['news']
    # Получаем все комментарии к новости.
    # Так они выводятся в шаблоне
    all_comments = news.comment_set.all()   
    # Проверяем, что время создания первого комментария в списке
    # меньше, чем время создания второго.
    assert all_comments[0].created < all_comments[1].created  

# Анонимному пользователю недоступна форма для отправки комментария 
# на странице отдельной новости, а авторизованному доступна.
@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, id_for_detail):
    url = reverse('news:detail', args=id_for_detail)
    response = client.get(url)                 
    assert 'form' not in  response.context


@pytest.mark.django_db     
def test_authorized_client_has_form(admin_client, id_for_detail):
    url = reverse('news:detail', args=id_for_detail)
    # Авторизуем клиент при помощи ранее созданного пользователя.
    response = admin_client.get(url)   
    assert 'form' in response.context 
