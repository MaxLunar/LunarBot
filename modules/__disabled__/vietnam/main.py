import os
import sys
import random
import requests
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse

def call(msg, **kw):
    try:
        message = kw['vk'].messages.getById(message_ids=int(kw['event'].message_id))
        photos = []
        for attach in message['items'][0]['attachments']:
            if attach['type'] == 'photo':
                photos.append(attach['photo'])
        p = photos[0]
        photo_url = p.get('photo_2560', p.get('photo_1280', p.get('photo_807', p.get('photo_604', p.get('photo_130', p.get('photo_75'))))))
    
        vk_photo = BytesIO()
        vk_photo.write(requests.get(photo_url, stream=True).raw.read())
        vk_photo.seek(0)
        vk_photo.name = 'photo' + os.path.splitext(urlparse(photo_url).path)[1]
        
        flashback = Image.open(VIET_DIR + random.choice(flash_list)).convert('RGBA')
        img = Image.open(vk_photo).convert('RGBA')
        flashback = flashback.resize(img.size)
        response = BytesIO()
        response.name = 'response.png'
        Image.blend(flashback, img, 0.75).save(response, 'PNG')
        response.seek(0)
    
        upload = vk_api.VkUpload(kw['vk_session'])
        photo = upload.photo_messages(response)
        resp = 'photo{0}_{1}'.format(photo[0]['owner_id'], photo[0]['id'])
    
        vk.messages.send(peer_id=event.peer_id), 
                    forward_messages=event.message_id,
                    message='Твоё фото:',
                    attachment=resp
                    )
    except Exception as err:
        print(err)
