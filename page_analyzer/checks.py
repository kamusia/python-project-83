from urllib.parse import urlparse
import validators


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
