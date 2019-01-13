# -*- coding: utf-8 -*-
import io
import re
import random
import vk_api
import requests
import traceback
from PIL import Image, ImageChops

methods = ('sum', 'sub', 'blend', 'min', 'max', 'diff', 'mul', 'screen')

documentation = """overlay - смесь режимами наложения из 2 пикч.
Доступные методы - {}""".format(methods)

access = 'user'


def call(**kw):
    vk = kw['vk']
    event = kw['event']
    vk_session = kw['vk_session']
    try:
        upload = vk_api.VkUpload(vk_session)
        msg = vk.messages.getById(message_ids=[event.message_id])['items'][0]
        photo_url_1 = None
        photo_url_2 = None
        attachments = msg.get('attachments', None)
        ticker = 0
        if attachments is not None:
            for attach in attachments:
                if attach['type'] == 'photo' and ticker < 2:
                    if ticker == 0:
                        ticker += 1
                        photo_url_1 = list(sorted(
                            attach['photo']['sizes'], key=lambda x: x['height'] + x['width']))[-1]['url']
                    elif ticker == 1:
                        ticker += 1
                        photo_url_2 = list(sorted(
                            attach['photo']['sizes'], key=lambda x: x['height'] + x['width']))[-1]['url']
        if photo_url_1 and photo_url_2:
            photo_download_1 = requests.get(photo_url_1, stream=True)
            photo_download_2 = requests.get(photo_url_2, stream=True)

            photo_download_1.raw.decode_content = True
            photo_download_2.raw.decode_content = True

            result = io.BytesIO()

            message = list(filter(None, event.text.lower().split()))[2:]
            method = None

            if message:
                method = message[0]
            else:
                method = 'blend'

            if method not in methods:
                method = 'blend'

            with Image.open(photo_download_1.raw) as photo1, Image.open(photo_download_2.raw) as photo2:
                photo2 = photo2.resize(photo1.size)
                photo1 = photo1.convert('RGB')
                photo2 = photo2.convert('RGB')

                res = None
                if method == 'blend':
                    res = ImageChops.blend(photo1, photo2, 0.5)
                elif method == 'sum':
                    res = ImageChops.add_modulo(photo1, photo2)
                elif method == 'sub':
                    res = ImageChops.subtract_modulo(photo1, photo2)
                elif method == 'min':
                    res = ImageChops.darker(photo1, photo2)
                elif method == 'max':
                    res = ImageChops.lighter(photo1, photo2)
                elif method == 'mul':
                    res = ImageChops.multiply(photo1, photo2)
                elif method == 'diff':
                    res = ImageChops.difference(photo1, photo2)
                elif method == 'screen':
                    res = ImageChops.screen(photo1, photo2)
                if res:
                    res.save(result, format='PNG')
                    result.seek(0)
                else:
                    return False
            response = upload.photo_messages(result)[0]

            attach_id = 'photo{0}_{1}'.format(
                response['owner_id'], response['id'])
            vk.messages.send(
                peer_id=event.peer_id,
                message='[id{0}|Твое] фото (mode = {1}):'.format(
                    event.user_id, method),
                random_id=random.randrange(2**32),
                attachment=attach_id,
            )
    except Exception as err:
        vk.messages.send(
            peer_id=event.peer_id,
            message='[ERROR]\n{0}'.format(traceback.format_exc()),
            random_id=random.randrange(2**32),
            forward_messages=event.message_id
        )
        return False
