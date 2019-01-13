# -*- coding: utf-8 -*-
import io
import random
import vk_api
import requests
import traceback

from collections import Counter
from random import choice, randint
from PIL import Image

documentation = """shift - разьебывает пикчу глитчами другим способом (best description ever)"""

access = 'user'


def call(**kw):
    vk = kw['vk']
    event = kw['event']
    vk_session = kw['vk_session']
    try:
        upload = vk_api.VkUpload(vk_session)
        message = list(filter(None, event.text.split()))
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
            result = io.BytesIO()
            with Image.open(photo_download.raw) as photo:
                a_bytes = photo.tobytes()
                target = None
                if len(message) > 2:
                    if message[2].isdigit():
                        if int(message[2]) in range(256):
                            target = bytes([int(message[2])])
                if not target:
                    byte_count = Counter(a_bytes)
                    target = tuple(
                        sorted(
                            byte_count.items(),
                            key=lambda x: x[1]))
                    target = bytes([target[-randint(1, 20)][0]])
                shifter = bytes((choice(a_bytes) for x in range(2)))
                b_bytes = a_bytes.replace(target, bytes(
                    (choice(a_bytes), choice(a_bytes))))
                img = Image.frombytes(
                    data=b_bytes, size=photo.size, mode=photo.mode)
                img.save(result, format='PNG')
                result.seek(0)
            response = upload.photo_messages(result)[0]
            vk.messages.send(
                peer_id=event.peer_id,
                message='[id{2}|Твое] фото (shift {0} to {1}):'.format(
                    repr(target), repr(shifter), event.user_id),
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
