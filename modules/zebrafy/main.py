# -*- coding: utf-8 -*-
import io
import random
import vk_api
import requests
import traceback
from random import randint, choice
from wand.image import Image

documentation = """zebrafy - разьебывает цвета пикчи"""

access = 'user'


def call(**kw):
    vk = kw['vk']
    event = kw['event']
    vk_session = kw['vk_session']
    try:
        upload = vk_api.VkUpload(vk_session)
        msg = vk.messages.getById(message_ids=[event.message_id])['items'][0]
        words = list(filter(None, event.text.split()))[2:]
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
            with Image(file=photo_download.raw) as photo:
                size = photo.size
                if not words:
                    coef_x = 3  # randint(1, 64)
                else:
                    try:
                        # pythonic clamp
                        coef_x = max(min(float(words[0]), 16.0), 1.0)
                    except BaseException:
                        coef_x = 3  # randint(2, 64)
                frequency = coef_x
                phase_shift = -90
                amplitude = 1.2
                bias = 0.5
                photo.function(
                    'sinusoid', [
                        frequency, phase_shift, amplitude, bias])
                photo.save(file=result)
            result.seek(0)
            response = upload.photo_messages(result)[0]
            vk.messages.send(
                peer_id=event.peer_id,
                message='[id{0}|Твое] фото: (freq = {1})'.format(
                    event.user_id, frequency),
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
