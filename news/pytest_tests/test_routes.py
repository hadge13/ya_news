import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects
from news.models import News
from django.urls import reverse

# анонимному пользователю доступна главная страница проекта, 
# страница отедльной новости, регистрации, входа и выхода
@pytest.mark.parametrize(
     'name, args', (
             ('news:home', None),
             ('users:signup', None),
             ('users:login', None),
             ('users:logout', None),
             ('news:detail', pytest.lazy_fixture('id_for_detail')))
) 

@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK

# Проверим, что автору комментария  доступны страницы  редактирования и удаления комментария,
#  а авторизованный пользователь не может зайти на страницы редактирования и удаления 
# чужих комментов (404)
@pytest.mark.parametrize(
    'parametrized_client, expected_status', (                                
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)    
        ),)

@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),)

def test_pages_availability_for_different_users(
    parametrized_client, name, comment, expected_status):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status

# При попытке перейти на страницу редактирования или удаления комментария
#  анонимный пользователь перенаправляется на страницу авторизации.

@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),)
def test_redirects(client, name, comment):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)