import psycopg2
import os
from dotenv import load_dotenv
from psycopg2.extras import DictCursor


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def get_all_urls():
    """
    Получает все URL из базы данных.
    Возвращает список словарей с полями:
    - id: идентификатор URL
    - name: имя сайта
    - last_check: дата последней проверки
    - status_code: код ответа
    """
    conn = get_db_connection()
    with conn.cursor(cursor_factory=DictCursor) as cur:
        query = """
        SELECT DISTINCT ON (urls.id)
            urls.id AS id,
            urls.name AS name,
            url_checks.created_at AS last_check,
            url_checks.status_code AS status_code
        FROM urls
        LEFT JOIN url_checks ON urls.id = url_checks.url_id
        AND url_checks.id = (SELECT MAX(id)
                            FROM url_checks
                            WHERE url_id = urls.id)
        ORDER BY urls.id DESC;
        """
        cur.execute(query)
    return cur.fetchall()


def add_url(url_name):
    """
    Добавляет новый URL в базу данных.
    Возвращает ID созданной записи или None если URL уже существует.
    """
    conn = get_db_connection()
    with conn.cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO urls (name) VALUES (%s) RETURNING id",
                (url_name,)
            )
            url_id = cur.fetchone()[0]
            conn.commit()
            return url_id
        except psycopg2.IntegrityError:  # Если URL уже существует
            conn.rollback()
            return None


def get_url_by_id(url_id):
    """
    Получает URL по его ID.
    Возвращает словарь с данными URL или None если не найден.
    """
    conn = get_db_connection()
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            "SELECT id, name, created_at FROM urls WHERE id = %s",
            (url_id,)
        )
        return cur.fetchone()


def get_url_by_name(url_name):
    """
    Получает URL по его имени.
    Возвращает словарь с данными URL или None если не найден.
    """
    conn = get_db_connection()
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(
            "SELECT id, name, created_at FROM urls WHERE name = %s",
            (url_name,)
        )
        return cur.fetchone()


def add_url_check(url_id, status_code=None, h1=None,
                  title=None, description=None):
    """
    Добавляет проверку URL с SEO-данными
    Возвращает ID созданной записи или None при ошибке
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO url_checks
                (url_id, status_code, h1, title, description)
                VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (url_id, status_code, h1, title, description)
            )
            check_id = cur.fetchone()[0]
            conn.commit()
            return check_id
    except Exception:
        conn.rollback()
        return None


def get_url_checks(url_id):
    """Получает все проверки URL с сортировкой по дате (новые сначала)"""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("""
            SELECT id, status_code, h1, title, description, created_at
            FROM url_checks
            WHERE url_id = %s
            ORDER BY created_at DESC
        """, (url_id,))
        return cur.fetchall()
