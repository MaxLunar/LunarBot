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
            result = [io.BytesIO() for _ in range(4)]
            raw_photo = photo_download.raw.read()
            raw_photos = [io.BytesIO() for _ in range(4)]
            for x in raw_photos:
                x.write(raw_photo)
                x.seek(0)
            for c in range(4):
                with Image.open(raw_photos[c]) as photo:
                    if c == 0:
                        img_half = photo.crop((0, 0, photo.width//2, photo.height))
                        img_flip = ImageOps.mirror(img_half)
                        photo.paste(img_flip, (photo.width//2, 0))
                    elif c == 1:
                        img_half = photo.crop((photo.width//2, 0, photo.width, photo.height))
                        img_flip = ImageOps.mirror(img_half)
                        photo.paste(img_flip, (0, 0))
                    elif c == 2:
                        img_half = photo.crop((0, 0, photo.width, photo.height//2))
                        img_flip = ImageOps.flip(img_half)
                        photo.paste(img_flip, (0, photo.height//2))
                    elif c == 3:
                        img_half = photo.crop((0, photo.height//2, photo.width, photo.height))
                        img_flip = ImageOps.flip(img_half)
                        photo.paste(img_flip, (0, 0))
                    photo.save(result[c], format='PNG')
                    result[c].seek(0)
                    raw_photos[c] = None

            response = ['photo{0}_{1}'.format(item['owner_id'], item['id']) for item in upload.photo_messages(result)]

            vk.messages.send(
                    peer_id=event.peer_id,
                    message='Твои фото:',
                    attachment=','.join(response)
                    )
                
                
    except Exception as err:
        vk.messages.send(
                peer_id=event.peer_id,
                message='[ERROR]\n{0}'.format(traceback.format_exc()),
                forward_messages=event.message_id
                )
        return False
