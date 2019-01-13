# -*- coding: utf-8 -*-
import io
import random
import vk_api
import requests
import traceback
from random import choice, randint
from wand.image import Image

documentation = """cas - разьебывает пикчу CAS'ом"""

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
                    try:
                        photo_url = list(sorted(
                            attach['photo']['sizes'], key=lambda x: x['height'] + x['width']))[-2]['url']
                    except BaseException:
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
                    coef_x = 2
                else:
                    try:
                        # pythonic clamp
                        coef_x = max(min(float(words[0]), 16.0), 1.0)
                    except BaseException:
                        coef_x = 2
                coef_x = float(coef_x)
                try:
                    int(coef_x)
                except BaseException:
                    coef_x = 2
                if choice((0, 1)) == 0:
                    ch = ('div', 'mul')
                    x_size = size[0] // coef_x
                    y_size = size[1] // coef_x
                else:
                    ch = ('mul', 'div')
                    x_size = size[0] // coef_x
                    y_size = size[1] // coef_x
                x_size, y_size = int(x_size), int(y_size)
                photo.liquid_rescale(x_size, y_size, delta_x=1)
                photo.sample(size[0], size[1])
                photo.save(file=result)
            result.seek(0)
            response = upload.photo_messages(result)[0]
            vk.messages.send(
                peer_id=event.peer_id,
                message='[id{5}|Твое] фото: ({0}x{1} => {2}x{3} (coef = div {4}) => {0}x{1})'.format(
                    size[0], size[1], x_size, y_size, coef_x, event.user_id),
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
