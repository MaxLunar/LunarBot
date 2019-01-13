# -*- coding: utf-8 -*-
import io
import random
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
                    photo_url = list(sorted(
                        attach['photo']['sizes'], key=lambda x: x['height'] + x['width']))[-1]['url']
                    break
        if photo_url is not None:
            photo_download = requests.get(photo_url, stream=True)
            photo_download.raw.decode_content = True
            result = io.BytesIO(photo_download.content)
            data = result.read()
            header_length = get_header_length(data)
            header, safe_data = data[:header_length], data[header_length:]
            ticker = True
            while ticker:
                try:
                    safe_data = safe_data.replace(
                        bytes([choice(data)]), bytes([choice(data)]))
                    proc = io.BytesIO(header + safe_data)
                    img = Image.open(proc)
                    final = io.BytesIO()
                    img.save(final, format='PNG')
                    final.seek(0)
                    ticker = 0
                except Exception as e:
                    ticker += 1
                    if ticker > 512:
                        raise e
                    else:
                        pass
            response = upload.photo_messages(final)[0]
            vk.messages.send(
                peer_id=event.peer_id,
                message='[id{0}|Твое] фото:'.format(event.user_id),
                random_id=random.randrange(2**32),
                attachment='photo{0}_{1}'.format(
                    response['owner_id'], response['id'])
            )

    except Exception as err:
        vk.messages.send(
            peer_id=event.peer_id,
            message='[ERROR]\n{0}'.format(traceback.format_exc()),
            random_id=random.randrange(2**32),
            forward_messages=event.message_id
        )
        return False
