from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
from page_analyzer.db import (get_all_urls, add_url, get_url_by_id,
                              get_url_by_name, add_url_check, get_url_checks)
from page_analyzer.checks import validate_url, get_url_data


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
        return render_template('index.html', url=raw_url,), 422

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

    except Exception:
        flash('Произошла ошибка при сохранении', 'danger')
        return redirect(url_for('index'))

    return redirect(url_for('show_url', id=url_id))


@app.get('/urls')
def show_urls():
    urls = get_all_urls()

    return render_template('urls.html', urls=urls)


@app.get('/urls/<int:id>')
def show_url(id):
    url = get_url_by_id(id)
    if not url:
        flash('Страница не найдена', 'danger')
        return redirect(url_for('index'))

    checks = get_url_checks(url['id'])

    return render_template('url.html', url=url, checks=checks)


@app.post('/urls/<int:id>/checks')
def check_url(id):
    url = get_url_by_id(id)

    check_data = get_url_data(url['name'])
    if not check_data:
        return redirect(url_for('show_url', id=id))

    # Используем существующую функцию
    check_id = add_url_check(
        url_id=id,
        status_code=check_data['status_code'],
        h1=check_data['h1'],
        title=check_data['title'],
        description=check_data['description']
    )

    if check_id:
        flash('Страница успешно проверена', 'success')
    else:
        flash('Ошибка при сохранении результатов проверки', 'danger')

    return redirect(url_for('show_url', id=id))
