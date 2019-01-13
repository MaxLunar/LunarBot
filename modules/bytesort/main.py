# -*- coding: utf-8 -*-
import io
import random
import vk_api
import requests
import traceback
import math

from PIL import Image

documentation = """bytesort - байтовое сортирование пикчи."""

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
            multiplier = None
            try:
                if len(message) > 2:
                    if int(message[2]) in range(2, 4096):
                        multiplier = int(message[2])
            except BaseException:
                pass
            if not multiplier:
                multiplier = 100

            result = io.BytesIO()
            with Image.open(photo_download.raw) as photo:
                a_bytes = photo.tobytes()
                orig_len = len(a_bytes)
                c_bytes = list(zip(*[iter(a_bytes)] * multiplier))
                b_bytes = []
                for x in c_bytes:
                    b_bytes.extend(sorted(x, key=lambda z: int(z)))
                b_bytes = bytes(b_bytes) + bytes(orig_len + len(b_bytes))
                img = Image.frombytes(
                    data=b_bytes, size=photo.size, mode=photo.mode)
                img.save(result, format='PNG')
                result.seek(0)
            response = upload.photo_messages(result)[0]
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
