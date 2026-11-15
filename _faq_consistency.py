"""Catch cross-page FAQ copy/paste and answer drift; not a clinical/content audit."""
import html
import json
import re

def normalize(value):
    return re.sub(r'\W+', '', html.unescape(re.sub(r'<[^>]+>', ' ', value))).casefold()

def objects(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from objects(item)
    elif isinstance(value, list):
        for item in value:
            yield from objects(item)

def check_faq(text, label):
    visible = re.sub(r'<(script|style|head|template)\b[^>]*>.*?</\1>', '', text, flags=re.S | re.I)
    visible = normalize(visible)
    count = 0
    for attrs, raw in re.findall(r'<script\b([^>]*)>(.*?)</script>', text, re.S | re.I):
        if not re.search(r'type\s*=\s*["\']application/ld\+json["\']', attrs, re.I):
            continue
        for obj in objects(json.loads(raw)):
            types = obj.get('@type', [])
            if isinstance(types, str):
                types = [types]
            if 'FAQPage' not in types:
                continue
            for question in obj.get('mainEntity', []):
                for value in (question.get('name', ''), question.get('acceptedAnswer', {}).get('text', '')):
                    if not normalize(value) or normalize(value) not in visible:
                        raise ValueError(f'FAQ content missing from page body: {label}: {value[:100]}')
                count += 1
    return count
