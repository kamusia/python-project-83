from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
import validators
from page_analyzer.db import get_db_connection


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def add_url():
    url = request.form['url']
    if not validators.url(url):
        flash('Некорректный URL', 'error')
        return redirect(url_for('index'))
    if len(url) > 255:
        flash('URL слишком длинный', 'error')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO urls (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id", (url,))
    url_id = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if url_id:
        flash('URL успешно добавлен', 'success')
        return redirect(url_for('show_url', id=url_id[0]))
    else:
        flash('URL уже существует', 'info')
        return redirect(url_for('show_url', id=cur.fetchone()[0]))


@app.get('/urls')
def show_urls():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM urls ORDER BY created_at DESC")
    urls = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('urls.html', urls=urls)


@app.get('/urls/<int:id>')
def show_url(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
    url = cur.fetchone()
    cur.close()
    conn.close()

    if url:
        return render_template('url.html', url=url)
    else:
        flash('URL не найден', 'error')
        return redirect(url_for('index'))
