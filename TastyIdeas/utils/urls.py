from typing import List

from django.urls import URLPattern


def filter_urls(urls: List[URLPattern], allowed_names: List[str]) -> List[URLPattern]:
    """
    Филтрира списък от URL шаблони базирано на техните имена.

    Параметри:
        urls : Списък от URL шаблони, които трябва да бъдат филтрирани.
        allowed_names : Списък от позволени имена на URL адреси.

    Връща:
        List[URLPattern] : Филтриран списък от URL шаблони с имена от списъка allowed_names.
    """
    filtered_urls = list(
        filter(lambda url: url.name in allowed_names, urls),
    )
    return filtered_urls