import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from .models import get_db_connection
import random
from datetime import datetime

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return redirect(url_for('main.login'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                query = (
                    "SELECT id, JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users')) AS name_users, JSON_UNQUOTE(JSON_EXTRACT(data, '$.password')) AS password "
                    "FROM users WHERE JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users')) = %s AND JSON_UNQUOTE(JSON_EXTRACT(data, '$.password')) = %s")
                cursor.execute(query, (username, password))
                result = cursor.fetchone()
                if result:
                    session['user'] = {
                        'id': result['id'],
                        'username': result['name_users']
                    }
                    return redirect(
                        url_for('main.warehouse_manager' if session['user']['username'] == current_app.config[
                            'ADMIN_NAME'] else 'main.profile'))

                else:
                    flash('Неверные учетные данные')
    return render_template('login.html')


@main.route('/logout')
def logout():
    session.pop('user', None)
    flash('Вы успешно вышли из системы')
    return redirect(url_for('main.login'))


@main.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('main.login'))

    username = session['user']['username']

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_consumables')) AS name_consumables, JSON_UNQUOTE(JSON_EXTRACT(data, '$.quantity')) AS quantity FROM consumables")
            consumables = cursor.fetchall()

            cursor.execute(
                "SELECT JSON_UNQUOTE(JSON_EXTRACT(data, '$.task')) AS task FROM tasks WHERE JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users')) = %s",
                (username,))
            tasks = cursor.fetchall()

    if request.method == 'POST':
        consumable_id = request.form['consumable_id']
        quantity_requested = int(request.form['quantity'])
        request_code = random.randint(100000, 999999)

        session['request'] = {
            "user": username,
            "consumable_id": consumable_id,
            "quantity_requested": quantity_requested,
            "request_code": request_code
        }

        return redirect(url_for('main.code', request_code=request_code))

    return render_template('profile.html', consumables=consumables, tasks=tasks, username=username)


@main.route('/code')
def code():
    request_code = request.args.get('request_code')
    if not request_code:
        return redirect(url_for('main.profile'))

    return render_template('code.html', request_code=request_code)


@main.route('/warehouse_manager', methods=['GET', 'POST'])
def warehouse_manager():
    if 'user' not in session or session['user']['username'] != current_app.config['ADMIN_NAME']:
        return redirect(url_for('main.login'))

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users')) AS name_users, JSON_UNQUOTE(JSON_EXTRACT(data, '$.password')) AS password FROM users")
            users = cursor.fetchall()

            cursor.execute(
                "SELECT id, JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_consumables')) AS name_consumables, JSON_UNQUOTE(JSON_EXTRACT(data, '$.quantity')) AS quantity FROM consumables")
            consumables = cursor.fetchall()

            cursor.execute(
                "SELECT JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users')) AS name_users, JSON_UNQUOTE(JSON_EXTRACT(data, '$.task')) AS task FROM tasks")
            tasks = cursor.fetchall()

            cursor.execute(
                "SELECT JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_users')) AS name_users, JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_consumables')) AS name_consumables, JSON_UNQUOTE(JSON_EXTRACT(data, '$.quantity')) AS quantity, JSON_UNQUOTE(JSON_EXTRACT(data, '$.time')) AS time FROM history_user")
            history_user = cursor.fetchall()

    request_data = None  # Инициализация request_data

    if request.method == 'POST':
        request_code = request.form['request_code']
        request_data = session.pop('request', None)

        if request_data and request_data['request_code'] == int(request_code):
            user = request_data['user']
            consumable_id = request_data['consumable_id']
            quantity_requested = request_data['quantity_requested']

            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, JSON_UNQUOTE(JSON_EXTRACT(data, '$.name_consumables')) AS name_consumables, JSON_UNQUOTE(JSON_EXTRACT(data, '$.quantity')) AS quantity FROM consumables WHERE id = %s",
                        (consumable_id,))
                    consumable = cursor.fetchone()

                    if consumable and int(
                            consumable['quantity']) >= quantity_requested:  # Преобразование quantity в int
                        new_quantity = int(consumable['quantity']) - quantity_requested

                        cursor.execute(
                            "UPDATE consumables SET data = JSON_SET(data, '$.quantity', %s) WHERE id = %s",
                            (new_quantity, consumable_id))
                        connection.commit()

                        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        cursor.execute("INSERT INTO history_user (data) VALUES (%s)", (json.dumps({
                            "name_users": user,
                            "name_consumables": consumable['name_consumables'],
                            "quantity": quantity_requested,
                            "time": now
                        }),))
                        connection.commit()

                        flash('Запрос выполнен успешно!')
                    else:
                        flash('Недостаточно расходных материалов на складе!')
        else:
            flash('Неверный код запроса!')

    return render_template('warehouse_manager.html', users=users, requests=[request_data] if request_data else [],
                           consumables=consumables, tasks=tasks, history_user=history_user)
