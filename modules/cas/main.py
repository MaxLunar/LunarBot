# -*- coding: utf-8 -*-
import io
import vk_api
import requests
import traceback
from random import choice
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
            result = io.BytesIO()
            with Image(file=photo_download.raw) as photo:
                size = photo.size
                coef_x = choice((2,3,4,5))
                coef_y = choice((2,3,4,5))
                if choice((0, 1)) == 0:
                    ch = ('div', 'mul')
                    x_size = size[0]//coef_x
                    y_size = size[1]*coef_y
                else:
                    ch = ('mul', 'div')
                    x_size = size[0]*coef_x
                    y_size = size[1]//coef_y
                photo.sample(x_size, y_size)
                photo.liquid_rescale(size[0], size[1])
                photo.save(file=result)
            result.seek(0)
            response = upload.photo_messages(result)[0]
            vk.messages.send(
                    peer_id=event.peer_id,
                    message='Твоё фото: ({0}x{1} => {2}x{3} (coef = [{6} {4}]x[{7} {5}]) => {0}x{1})'.format(size[0], size[1], x_size, y_size, coef_x, coef_y, ch[0], ch[1]),
                    forward_messages=event.message_id,
                    attachment='photo{0}_{1}'.format(response['owner_id'], response['id'])
                    )
                
                
    except Exception as err:
        vk.messages.send(
                peer_id=event.peer_id,
                message='[ERROR]\n{0}'.format(traceback.format_exc()),
                forward_messages=event.message_id
                )
        return False
