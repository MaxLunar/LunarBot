# -*- coding: utf-8 -*-
import io
import random
import vk_api
import requests
import traceback
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

documentation = """deepfrier - прожигает пикчу до состояния рака &#128514;&#128076;"""

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
                    photo_url = list(sorted(
                        attach['photo']['sizes'], key=lambda x: x['height'] + x['width']))[-1]['url']
                    break
        if photo_url is not None:
            photo_download = requests.get(photo_url, stream=True)
            photo_download.raw.decode_content = True
            result = io.BytesIO()
            with Image.open(photo_download.raw) as img_orig:
                img = img_orig.copy().convert('RGB')
                width, height = img.width, img.height
                img = img.resize(
                    (int(width ** .75), int(height ** .75)), resample=Image.LANCZOS)
                img = img.resize(
                    (int(width ** .88), int(height ** .88)), resample=Image.BILINEAR)
                img = img.resize(
                    (int(width ** .9), int(height ** .9)), resample=Image.BICUBIC)
                img = img.resize((width, height), resample=Image.BICUBIC)

                r = img.split()[0]
                r = ImageEnhance.Contrast(r).enhance(2.0)
                r = ImageEnhance.Brightness(r).enhance(1.5)
                r = ImageOps.colorize(r, (254, 0, 2), (255, 255, 15))

                img = Image.blend(img, img_orig, 0.4)
                img = Image.blend(img, r, 0.3)
                img = ImageEnhance.Sharpness(img).enhance(200.0)

                img = img.filter(
                    ImageFilter.UnsharpMask(
                        radius=7,
                        percent=2500,
                        threshold=0))
                img.save(result, format="JPEG", quality=10)
            result.seek(0)
            response = upload.photo_messages(result)[0]
            vk.messages.send(
                peer_id=event.peer_id,
                message='[id{0}|Твое] фото &#128514;&#128076;:'.format(
                    event.user_id),
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
