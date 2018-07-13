# -*- coding: utf-8 -*-
import io
import vk_api
import requests
import traceback

from random import choice
from PIL import Image

documentation = """mult - почкование пикчи."""

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
                    photo_url = attach['photo'].get('photo_2560', attach['photo'].get('photo_1280', attach['photo'].get('photo_807', attach['photo'].get('photo_604', attach['photo'].get('photo_130', attach['photo'].get('photo_75', None))))))
                    break
        if photo_url is not None:
            photo_download = requests.get(photo_url, stream=True)
            photo_download.raw.decode_content = True
            multiplier = None
            try:
                if len(message) > 2:
                    if int(message[2]) != 0 and int(message[2]) in range(-65536, 65536):
                        multiplier = int(message[2])
            except:
                pass
            if not multiplier:
                multiplier = 2
                
            result = io.BytesIO()
            with Image.open(photo_download.raw) as photo:
                a_bytes = photo.tobytes()
                b_bytes = a_bytes[::multiplier]*abs(multiplier)
                img = Image.frombytes(data=b_bytes, size=photo.size, mode=photo.mode)
                img.save(result, format='PNG')
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
