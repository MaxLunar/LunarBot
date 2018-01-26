# -*- coding: utf-8 -*-
import io
import vk_api
import requests
import traceback

from random import choice
from PIL import Image
from itertools import tee

documentation = """glitch - разьебывает пикчу глитчами"""

access = 'user'
def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def get_header_length(bts):
    for i, pair in enumerate(pairwise(bts)):
        if pair[0] == 255 and pair[1] == 218:
            result = i + 2
            return result

def call(**kw):
    vk = kw['vk']
    event = kw['event']
    vk_session = kw['vk_session']
    try:
        upload = vk_api.VkUpload(vk_session)
        msg = vk.messages.getById(message_ids=[event.message_id])['items'][0]
        photo_url = None
        attachments = msg.get('attachments', None)
        if attachments is not None:
            for attach in attachments:
                if attach['type'] == 'photo':
                    photo_url = attach['photo'].get('photo_2560', attach['photo'].get('photo_1280', attach['photo'].get('photo_807', attach['photo'].get('photo_604', attach['photo'].get('photo_130', attach['photo'].get('photo_75', None))))))
                    break
        if photo_url is not None:
            photo_download = requests.get(photo_url, stream=True)
            photo_download.raw.decode_content = True
            result = io.BytesIO(photo_download.content)
            data = result.read()
            header_length = get_header_length(data)
            header, safe_data = data[:header_length], data[header_length:]
            safe_data = safe_data.replace(bytes([choice(data)]), bytes([choice(data)]))
            proc = io.BytesIO(header+safe_data)
            img = Image.open(proc)
            final = io.BytesIO()
            img.save(final, format='PNG')
            final.seek(0)
            response = upload.photo_messages(final)[0]
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
