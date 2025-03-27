from urllib.parse import urlparse
import validators
import requests
from bs4 import BeautifulSoup
from flask import flash


def validate_url(url):
    """
    Проверяет и нормализует URL.
    Возвращает кортеж: (нормализованный_url, список_ошибок)
    """
    errors = []
    normalized_url = url.strip() if url else ''

    if not normalized_url:
        errors.append('URL обязателен для заполнения')
        return None, errors

    if not urlparse(normalized_url).scheme:
        normalized_url = f'https://{normalized_url}'

    if not validators.url(normalized_url):
        errors.append('Некорректный URL')

    if len(normalized_url) > 255:
        errors.append('URL превышает 255 символов')

    return normalized_url if not errors else None, errors


def get_url_data(url):
    """
    Выполняет проверку сайта и возвращает данные
    или None при ошибке:
    {
        'status_code': int,
        'h1': str | None,
        'title': str | None,
        'description': str | None
    }
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Проверяет HTTP-ошибки (4xx/5xx)

        soup = BeautifulSoup(response.text, 'html.parser')

        return {
            'status_code': response.status_code,
            'h1': soup.h1.get_text().strip()[:255] if soup.h1 else None,
            'title': soup.title.string.strip()[:255] if soup.title else None,
            'description': (
                soup.find('meta', attrs={'name': 'description'})[
                    'content'].strip()[:255]
                if soup.find('meta', attrs={'name': 'description'}) else None
            )
        }

    except requests.RequestException as e:
        flash(f'Ошибка при проверке сайта', 'danger')
        return None
