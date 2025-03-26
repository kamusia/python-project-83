from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
import validators
from page_analyzer.db import get_all_urls, add_url, get_url_by_id, get_url_by_name, add_url_check, get_url_checks
from page_analyzer.checks import validate_url
from psycopg2.extras import DictCursor


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def post_url():
    # Получаем и валидируем URL
    raw_url = request.form.get('url')
    normalized_url, errors = validate_url(raw_url)

    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('index'))

    try:
        url_id = add_url(normalized_url)

        if url_id:  # URL был добавлен
            flash('Страница успешно добавлена', 'success')
        else:  # URL уже существует
            existing_url = get_url_by_name(normalized_url)
            if not existing_url:
                flash('Ошибка базы данных', 'danger')
                return redirect(url_for('index'))

            flash('Страница уже существует', 'info')
            url_id = existing_url['id']

    except Exception as e:  # Обработка ошибок БД
        flash('Произошла ошибка при сохранении', 'danger')
        return redirect(url_for('index'))

    return redirect(url_for('show_url', id=url_id))


@app.get('/urls')
def show_urls():
    urls = get_all_urls()

    for url in urls:
        checks = get_url_checks(url['id'])
        if checks:
            url['last_check'] = checks[0]['created_at']
            url['status_code'] = checks[0]['status_code']

    return render_template('urls.html', urls=urls)


@app.get('/urls/<int:id>')
def show_url(id):
    url = get_url_by_id(id)
    if not url:
        flash('Страница не найдена', 'danger')
        return redirect(url_for('index'))
    return render_template('url.html', url=url)


@app.post('/urls/<int:id>/checks')
def check_url(id):
    try:
        check_id = add_url_check(id)
        flash('Страница успешно проверена', 'success')
    except Exception as e:
        flash('Произошла ошибка при проверке', 'danger')

    return redirect(url_for('show_url', id=id))
