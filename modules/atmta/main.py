# -*- coding: utf-8 -*-
import io
import vk_api
import requests
import traceback
from PIL import Image, ImageOps

documentation = """atmta/xymyx - зеркалит пикчу."""

access = 'user'
def call(**kw):
    vk = kw['vk']
    event = kw['event']
    vk_session = kw['vk_session']
    try:
        msg = list(filter(None, event.text.split()))
        mode = msg[1]
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
            with Image.open(photo_download.raw) as photo:
                if mode == 'xymyx':
                    img_half = photo.crop((0, 0, photo.width//2, photo.height))
                    img_flip = ImageOps.mirror(img_half)
                    photo.paste(img_flip, (photo.width//2, 0))
                elif mode == 'atmta':
                    img_half = photo.crop((photo.width//2, 0, photo.width, photo.height))
                    img_flip = ImageOps.mirror(img_half)
                    photo.paste(img_flip, (0, 0))
                photo.save(result, format='PNG')
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
