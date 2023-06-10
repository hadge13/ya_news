from django.urls import reverse
from django.conf import settings
from datetime import datetime, timedelta 
from django.utils import timezone
import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError
from news.models import News, Comment
from news.forms import BAD_WORDS, WARNING


# Анонимный пользователь не может отправить комментарий, 
@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data_comment, id_for_detail):
    url = reverse('news:detail', args=id_for_detail)
    # Через анонимный клиент пытаемся создать заметку:
    response = client.post(url, data=form_data_comment)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    # Проверяем, что произошла переадресация на страницу логина:
    assertRedirects(response, expected_url)
    # Считаем количество заметок в БД, ожидаем 0 заметок.
    assert Comment.objects.count() == 0 

# Авторизованный пользователь может отправить комментарий
@pytest.mark.django_db
def test_user_can_create_comment(news, admin_client, author_client, form_data_comment, id_for_detail):
    url = reverse('news:detail', args=id_for_detail)
    # Через анонимный клиент создаем комментарий:
    response = admin_client.post(url, data=form_data_comment)
    # Проверяем, что был выполнен редирект на страницу успешного добавления комментария:
    assertRedirects(response, f'{url}#comments')
    # Считаем общее количество комментов в БД, ожидаем 1 комментарий.
    assert Comment.objects.count() == 1
    # Чтобы проверить значения комментария - 
    # получаем его из базы при помощи метода get():
    comment = Comment.objects.get()
    # Сверяем атрибуты объекта с ожидаемыми.
    assert comment.text == form_data_comment['text']
    assert comment.news == news

    # print(comment.author, author_client)
    # assert comment.author == author_client

# Авторизованный пользователь может редактировать свои комментарии
@pytest.mark.django_db
def test_author_can_edit_comment(author_client, form_data_comment, comment, id_for_detail):
    # Получаем адрес страницы детализации:
    url = reverse('news:detail', args=id_for_detail)
    # Получаем адрес страницы редактирования комментария:
    url_to_comment = url + '#comments'
    edit_url = reverse('news:edit', args=(comment.id,))
    # В POST-запросе на адрес редактирования комментария
    # отправляем form_data_comment - новые значения для полей комментиря:
    response = author_client.post(edit_url, form_data_comment)
    # Проверяем редирект:
    assertRedirects(response, url_to_comment)
    # Обновляем объект комментария: получаем обновлённые данные из БД:
    comment.refresh_from_db()
    # Проверяем, что атрибуты комментария соответствуют обновлённым:
    assert comment.text == form_data_comment['text']

# Авторизованный пользователь может удалять свои комментарии   
@pytest.mark.django_db
def test_author_can_delete_comment(author_client, form_data_comment, comment, id_for_detail):
    # Получаем адрес страницы детализации:
    url = reverse('news:detail', args=id_for_detail)
    # Получаем адрес страницы удаления комментария:
    url_to_comment = url + '#comments'
    delete_url = reverse('news:delete', args=(comment.id,))
    # В POST-запросе на адрес редактирования комментария
    # отправляем form_data_comment - новые значения для полей комментиря:
    response = author_client.post(delete_url, form_data_comment)
    # Проверяем редирект:
    assertRedirects(response, url_to_comment)
    assert Comment.objects.count() == 0

# Авторизованный пользователь не может редактировать чужие комментарии
@pytest.mark.django_db
def test_user_can_edit_comment(admin_client, form_data_comment, comment, id_for_detail):
    # Получаем адрес страницы детализации:
    # url = reverse('news:detail', args=id_for_detail)
    # Получаем адрес страницы редактирования комментария:
    edit_url = reverse('news:edit', args=(comment.id,))
    print(edit_url)
    # В POST-запросе на адрес редактирования комментария
    # отправляем form_data_comment - новые значения для полей комментиря:
    response = admin_client.post(edit_url, form_data_comment)
   # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    comment_from_db = Comment.objects.get(id=comment.id)
    print(comment_from_db)
    # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
    assert comment.text == comment_from_db.text
    print(comment)
 
# Авторизованный пользователь не может удалять чужие комментарии   
@pytest.mark.django_db
def test_user_can_delete_comment(admin_client, form_data_comment, comment):
    delete_url = reverse('news:delete', args=(comment.id,))
    # В POST-запросе на адрес редактирования комментария
    # отправляем form_data_comment - новые значения для полей комментиря:
    response = admin_client.post(delete_url, form_data_comment)
    # Проверяем редирект:
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1

# Проверка блокировки стоп-слов в комментарии
def test_user_cant_use_bad_words(admin_client, id_for_detail):
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    url = reverse('news:detail', args=id_for_detail)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    response = admin_client.post(url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    # assert 'form' not in  response.context
    # assertFormError(response,
    #     form='form',
    #     field='text',
    #     errors=WARNING) 
    assert WARNING in response.context['form'].errors['text']
    comments_count = Comment.objects.count()
    assert comments_count == 0
    
    
    
    # assert FormError(
    #     response,
    #     form='form',
    #     field='text',
    #     errors=WARNING
    # )
    