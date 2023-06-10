import pytest
# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import News, Comment
from datetime import datetime, timedelta 
from django.utils import timezone
from django.conf import settings

# Фикстура новости
@pytest.fixture
def news():
    return News.objects.create(
        title = 'Заголовок', 
        text = 'Текст', 
        )

@pytest.fixture
def id_for_detail(news):
    return news.id,


# Фикстура автора комментария
@pytest.fixture
def author(django_user_model):  
    return django_user_model.objects.create(username='Автор комментария')

# Логиним автора в клиенте
@pytest.fixture
def author_client(author, client):  
    client.force_login(author)  
    return client   

# Фикстура комментария
@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(  
        news=news,
        text='Текст комментария',
        author=author,)
    return comment

# Фикстура 11 новостей на странице
@pytest.fixture
def eleven_news_on_page(news):
    today = datetime.today()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(title=f'Новость {index}', text='Просто текст.', date=today - timedelta(days=index))
        all_news.append(news)
    list_news_eleven = News.objects.bulk_create(all_news)
    return list_news_eleven

# Комментарии еще одна версия
@pytest.fixture
def comments_for_time(news, author):
    now = timezone.now()
    for index in range(2):
        comment_for_time = Comment.objects.create( 
            news=news,
            text=f'Tекст {index}',
            author=author,
    )
        comment_for_time.created = now + timedelta(days=index)
    return comment_for_time

# Форма для комментария
@pytest.fixture
def form_data_comment():
    return {
        'text': 'Новый текст комментария',
    }