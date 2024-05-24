# -*- coding: utf-8 -*-
"""Маршруты в веб сервисе.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1d4ZbRICu9K26ZX6ctV_aFDIssIg9oKB8

# **Импорт библиотек и модулей**
"""

import json

"""Импортируем модуль json для работы с JSON-данными.


"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app

"""Импортируем необходимые функции и классы из Flask: Blueprint для создания блупринта, render_template для рендеринга HTML-шаблонов, request для работы с данными запроса, redirect для перенаправления пользователя, url_for для построения URL по имени маршрута, flash для отображения временных сообщений пользователю, session для работы с сессиями и current_app для доступа к текущему приложению."""

from .models import get_db_connection

"""Импортируем функцию get_db_connection из модуля models, которая используется для получения соединения с базой данных."""

import random

"""Импортируем модуль random для генерации случайных чисел. пригодится когда будем создавать 6-ти значный код для получения расходника со склада (как в пункте выдачи Ozon, пользователю необходимо сказать 6 цифр чтобы товар списался со склада)"""

from datetime import datetime

"""Импортируем datetime из модуля datetime для работы с датой и временем. (время получения расходника)

# **Создание блупринта**
"""

main = Blueprint('main', __name__)

"""Создаем блупринт main, который будет содержать все маршруты приложения.

# **Маршрут для перенаправления на страницу логина**
"""

@main.route('/')

"""Декоратор для маршрута /."""

def index():

"""Определяем функцию index."""

return redirect(url_for('main.login'))

"""Перенаправляем пользователя на страницу логина.

# **Маршрут для логина**
"""

@main.route('/login', methods=['GET', 'POST'])

"""Декоратор для маршрута /login, поддерживает методы GET и POST.


"""

def login():

"""Определяем функцию login."""

if request.method == 'POST':

"""Проверяем, является ли метод запроса POST."""

username = request.form['username']

"""Извлекаем значение password из данных формы."""

with get_db_connection() as connection:

"""Получаем соединение с базой данных."""

with connection.cursor() as cursor:

"""Создаем курсор для выполнения запросов к базе данных."""

query = (
                    "SELECT id, JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users')) AS name_users, JSON_UNQUOTE(JSON_EXTRACT(data, '$.password')) AS password "
                    "FROM users WHERE JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users')) = %s AND JSON_UNQUOTE(JSON_EXTRACT(data, '$.password')) = %s")

"""Определяем SQL-запрос для проверки учетных данных пользователя.


"""

cursor.execute(query, (username, password))

"""Выполняем SQL-запрос с параметрами username и password."""

result = cursor.fetchone()

"""Получаем результат запроса.


"""

if result:

"""Проверяем, найден ли пользователь."""

session['user'] = {
                        'id': result['id'],
                        'username': result['name_users']
                    }

"""Если пользователь найден, сохраняем его данные в сессии."""

return redirect(
                        url_for('main.warehouse_manager' if session['user']['username'] == current_app.config['ADMIN_NAME'] else 'main.profile'))

"""Перенаправляем пользователя на страницу управления складом или на страницу профиля в зависимости от имени пользователя (по дефолту админом является менеджер склада (зав хоз) (Manager - 1111) )."""

else:
                    flash('Неверные учетные данные')

"""Если пользователь не найден, отображаем сообщение об ошибке."""

return render_template('login.html')

"""Если метод запроса GET, отображаем форму логина.

# **Маршрут для выхода из системы**
"""

@main.route('/logout')

"""Декоратор для маршрута /logout."""

def logout():

"""Определяем функцию logout."""

session.pop('user', None)

"""Удаляем данные пользователя из сессии."""

flash('Вы успешно вышли из системы')

"""Отображаем сообщение о выходе."""

return redirect(url_for('main.login'))

"""Перенаправляем на страницу логина.

# **Маршрут для профиля пользователя**
"""

@main.route('/profile', methods=['GET', 'POST'])

"""Декоратор для маршрута /profile, поддерживает методы GET и POST.


"""

def profile():

"""Определяем функцию profile для обычных смертных"""

if 'user' not in session:

"""Проверяем, есть ли пользователь в сессии."""

return redirect(url_for('main.login'))

"""Если пользователя нет в сессии, перенаправляем на страницу логина.


"""

username = session['user']['username']

"""Извлекаем username из сессии."""

with get_db_connection() as connection:

"""Получаем соединение с базой данных."""

with connection.cursor() as cursor:

"""Создаем курсор для выполнения запросов к базе данных."""

cursor.execute(
                "SELECT id, JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_consumables')) AS name_consumables, JSON_UNQUOTE(JSON_EXTRACT(data, '$.quantity')) AS quantity FROM consumables")

"""Выполняем SQL-запрос для извлечения информации о расходниках."""

consumables = cursor.fetchall()

"""Получаем результат запроса."""

cursor.execute(
                "SELECT JSON_UNQUOTE(JSON_EXTRACT(data, '$.task')) AS task FROM tasks WHERE JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users')) = %s",
                (username,))

"""Выполняем SQL-запрос для извлечения задач пользователя."""

tasks = cursor.fetchall()

"""Получаем результат запроса о ежедневных задачах сотрудников."""

if request.method == 'POST':

"""Проверяем, является ли метод запроса POST. (это когда мы выбираем расходник и нажимаем на кнопку получить)"""

consumable_id = request.form['consumable_id']

"""Извлекаем значение consumable_id (название расходника, вроде название, ну может это номер по списку, но в итоге получим название в таблице) из данных формы."""

quantity_requested = int(request.form['quantity'])

"""Извлекаем значение quantity из данных формы и преобразуем его в целое число.

(количество пельменей, которые мы хотим взять со склада)
"""

request_code = random.randint(100000, 999999)

"""Генерируем случайный request_code. (код запроса для получения расходника)"""

session['request'] = {
            "user": username,
            "consumable_id": consumable_id,
            "quantity_requested": quantity_requested,
            "request_code": request_code
        }

"""Сохраняем запрос в сессии."""

return redirect(url_for('main.code', request_code=request_code))

"""Перенаправляем на страницу с кодом запроса."""

return render_template('profile.html', consumables=consumables, tasks=tasks, username=username)

"""Если метод запроса GET, отображаем профиль пользователя с информацией о расходниках и задачах.

# **Маршрут для отображения кода запроса**
"""

@main.route('/code')

"""Декоратор для маршрута /code"""

def code():

"""Определяем функцию code."""

request_code = request.args.get('request_code')

"""Извлекаем значение request_code из параметров запроса.


"""

if not request_code:

"""Проверяем, существует ли request_code.


"""

return redirect(url_for('main.profile'))

"""Если request_code отсутствует, перенаправляем на страницу профиля.


"""

return render_template('code.html', request_code=request_code)

"""Если request_code присутствует, отображаем страницу с кодом запроса.

# **Маршрут для управления складом**
"""

@main.route('/warehouse_manager', methods=['GET', 'POST'])

"""Декоратор для маршрута /warehouse_manager, поддерживает методы GET и POST. Админская страница


"""

def warehouse_manager():

"""Определяем функцию warehouse_manager.


"""

if 'user' not in session or session['user']['username'] != current_app.config['ADMIN_NAME']:

"""Проверяем, есть ли пользователь в сессии и является ли он администратором.


"""

return redirect(url_for('main.login'))

"""Если пользователя нет в сессии или он не является администратором, перенаправляем на страницу логина."""

with get_db_connection() as connection:

"""Получаем соединение с базой данных.


"""

with connection.cursor() as cursor:

"""Создаем курсор для выполнения запросов к базе данных.


"""

cursor.execute(
                "SELECT id, JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users')) AS name_users, JSON_UNQUOTE(JSON_EXTRACT(data, '$.password')) AS password FROM users")

"""Выполняем SQL-запрос для извлечения информации о пользователях.


"""

users = cursor.fetchall()

"""Получаем результат запроса.


"""

cursor.execute(
                "SELECT id, JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_consumables')) AS name_consumables, JSON_UNQUOTE(JSON_EXTRACT(data, '$.quantity')) AS quantity FROM consumables")

"""Выполняем SQL-запрос для извлечения информации о расходниках.


"""

consumables = cursor.fetchall()

"""Получаем результат запроса.


"""

cursor.execute(
                "SELECT JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users')) AS name_users, JSON_UNQUOTE(JSON_EXTRACT(data, '$.task')) AS task FROM tasks")

"""Выполняем SQL-запрос для извлечения информации о задачах сотрудников.


"""

tasks = cursor.fetchall()

"""Получаем результат запроса.


"""

cursor.execute(
                "SELECT JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users')) AS name_users, JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_consumables')) AS name_consumables, JSON_UNQUOTE(JSON_EXTRACT(data, '$.quantity')) AS quantity, JSON_UNQUOTE(JSON_EXTRACT(data, '$.time')) AS time FROM history_user")

"""Выполняем SQL-запрос для извлечения истории выдачи расходников со склада (кто взял, что взял, сколько взял и во сколько это взял (время)).


"""

history_user = cursor.fetchall()

"""Получаем результат запроса.


"""

request_data = None

"""Инициализируем переменную request_data.


"""

if request.method == 'POST':

"""Проверяем, является ли метод запроса POST.


"""

request_code = request.form['request_code']

"""Извлекаем значение request_code из данных формы.


"""

request_data = session.pop('request', None)

"""Извлекаем запрос из сессии и удаляем его.

"""

if request_data and request_data['request_code'] == int(request_code):

"""Проверяем, существует ли запрос и совпадает ли код запроса.


"""

user = request_data['user']

"""Извлекаем значение user из запроса.


"""

consumable_id = request_data['consumable_id']

"""Извлекаем значение consumable_id из запроса.


"""

quantity_requested = request_data['quantity_requested']

"""Извлекаем значение quantity_requested из запроса.


"""

with get_db_connection() as connection:

"""Получаем соединение с базой данных.


"""

with connection.cursor() as cursor:

"""Создаем курсор для выполнения запросов к базе данных.


"""

cursor.execute(
                        "SELECT id, JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_consumables')) AS name_consumables, JSON_UNQUOTE(JSON_EXTRACT(data, '$.quantity')) AS quantity FROM consumables WHERE id = %s",
                        (consumable_id,))

"""Выполняем SQL-запрос для извлечения информации о конкретном расходнике.


"""

consumable = cursor.fetchone()

"""Получаем результат запроса.


"""

if consumable and int(consumable['quantity']) >= quantity_requested:

"""Проверяем, существует ли расходник и достаточно ли его количества.


"""

new_quantity = int(consumable['quantity']) - quantity_requested

"""Вычисляем новое количество расходника.


"""

cursor.execute(
                            "UPDATE consumables SET data = JSON_SET(data, '$.quantity', %s) WHERE id = %s",
                            (new_quantity, consumable_id))

"""Выполняем SQL-запрос для обновления количества расходника в базе данных.


"""

connection.commit()

"""Подтверждаем изменения в базе данных.


"""

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

"""Получаем текущее время в формате строки.


"""

cursor.execute("INSERT INTO history_user (data) VALUES (%s)", (json.dumps({
                            "name_users": user,
                            "name_consumables": consumable['name_consumables'],
                            "quantity": quantity_requested,
                            "time": now
                        }),))

"""Выполняем SQL-запрос для добавления записи в историю выдачи расходников.


"""

connection.commit()

"""Подтверждаем изменения в базе данных.


"""

flash('Запрос выполнен успешно!')

"""Отображаем сообщение об успешном выполнении запроса.


"""

else:
                        flash('Недостаточно расходных материалов на складе!')

"""Если недостаточно расходных материалов, отображаем сообщение об ошибке.


"""

else:
            flash('Неверный код запроса!')

"""Если запрос не найден или код не совпадает, отображаем сообщение об ошибке.


"""

return render_template('warehouse_manager.html', users=users, requests=[request_data] if request_data else [],
                           consumables=consumables, tasks=tasks, history_user=history_user)

"""Если метод запроса GET, отображаем страницу управления складом с информацией о пользователях, расходниках, задачах и истории выдачи."""