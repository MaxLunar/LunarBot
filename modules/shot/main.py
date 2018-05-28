# -*- coding: utf-8 -*-
import io
import base64
import vk_api
import requests
import traceback
from wand.image import Image

documentation = """shot - скриншотилка сайтов. Использование - L shot <url> [size]"""

access = 'superadmin'
def call(**kw):
    vk = kw['vk']
    event = kw['event']
    vk_session = kw['vk_session']
    driver = kw['bot'].utilities['webdriver']
    try:
        upload = vk_api.VkUpload(vk_session)
        msg = list(filter(None, event.text.split()))[2:]
        if msg:
            url = msg[0]
            if not url.startswith('http'):
                url = 'http://' + url
        else:
            url = None
        if len(msg) >= 2:
            if 'x' in msg[1]:
                size = msg[1].split('x')
            elif 'х' in msg[1]:
                size = msg[1].split('х')
        else:
            size = [1280, 720]
        if url:
            driver.get(url)
        if driver.current_url == 'about:blank':
            return
        driver.set_window_size(size[0], size[1])
        img = base64.b64decode(driver.get_screenshot_as_base64())
        result = io.BytesIO()
        with Image(blob=img) as photo:
            photo.save(file=result)
        result.seek(0)
        response = upload.photo_messages(result)[0]
        vk.messages.send(
                peer_id=event.peer_id,
                message='Твоё фото:',
                attachment='photo{0}_{1}'.format(response['owner_id'], response['id'])
                )
                
                
    except Exception as err:
        vk.messages.send(
                peer_id=event.peer_id,
                message='[ERROR]\n{0}'.format(traceback.format_exc()),
                forward_messages=event.message_id
                )
        return False
