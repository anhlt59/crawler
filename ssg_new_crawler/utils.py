# -*- coding: utf-8 -*-
import logging
import time
import hashlib
import requests


logger = logging.getLogger(__name__)
logger.setLevel('ERROR')


def strstrip(text):
    return re.sub(r'^[^\d\w]+|[^\d\w]+$',   '', text) if text else ''


def strmd5(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest() if text else ''


def mapcompose(obj, *func):
    return mapcompose(func[0](obj), *func[1:]) if func else obj


def download_img(image_url, dtype='news', size=1, url='https://xemgiaca.com/upload/image', cdn='{cdn}'):
    data = {
        'data': image_url,
        'type': dtype,
        'size': size
    }
    req = requests.post(url, data=data, verify=False)
    return f"{cdn}{req.content.decode('utf-8')}" if req.content.decode('utf-8') != 'Error' else None


def cookie_to_har(cookie):
    """Convert a Cookie instance to a dict in HAR cookie format"""
    c = {
        'name': cookie.name,
        'value': cookie.value,
        'secure': cookie.secure,
    }
    if cookie.path_specified:
        c['path'] = cookie.path
    if cookie.domain_specified:
        c['domain'] = cookie.domain
    if cookie.expires:
        tm = time.gmtime(cookie.expires)
        c['expires'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", tm)

    http_only = cookie.get_nonstandard_attr('HttpOnly')
    if http_only is not None:
        c['httpOnly'] = bool(http_only)
    if cookie.comment:
        c['comment'] = cookie.comment

    return c
