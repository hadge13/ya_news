# news/tests/test_trial.py
from django.test import TestCase
import unittest

# Импортируем модель, чтобы работать с ней в тестах.
from news.models import News


# Создаём тестовый класс с произвольным названием, наследуем его от TestCase.
@unittest.skip(reason='bla')
class TestNews(TestCase):

    # Все нужные переменные сохраняем в атрибуты класса.
    TITLE = 'Заголовок новости'
    TEXT = 'Тестовый текст'

    # В методе класса setUpTestData создаём тестовые объекты.
    # Оборачиваем метод соответствующим декоратором.    
    
    @classmethod
    def setUpTestData(cls):
        # Стандартным методом Django ORM create() создаём объект класса.
        # Присваиваем объект атрибуту класса: назовём его news.
        cls.news = News.objects.create(
            # title='Заголовок новости',
            # text='Тестовый текст',
            # При создании объекта обращаемся к константам класса через cls.
            title=cls.TITLE,
            text=cls.TEXT,
        )
        

    # Проверим, что объект действительно было создан.
    def test_successful_creation(self):
        # При помощи обычного ORM-метода посчитаем количество записей в базе.
        news_count = News.objects.count()
        # Сравним полученное число с единицей.
        self.assertEqual(news_count, 1)


    def test_title(self):
        # Сравним свойство объекта и ожидаемое значение.
        # self.assertEqual(self.news.title, 'Заголовок новости')
        self.assertEqual(self.news.title, self.TITLE)   