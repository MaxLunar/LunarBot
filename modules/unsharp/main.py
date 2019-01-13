# -*- coding: utf-8 -*-
import io
import random
import vk_api
import requests
import traceback
from PIL import Image, ImageFilter

documentation = """unsharp - разьебывает пикчу аншарп маской."""

access = 'user'


def call(**kw):
    vk = kw['vk']
    event = kw['event']
    vk_session = kw['vk_session']
    try:
        upload = vk_api.VkUpload(vk_session)
        words = list(filter(None, event.text.split()))[2:]
        if not words:
            amount = 5000
            rad = 1
        else:
            if len(words) == 1:
                rad = 1
            else:
                try:
                    rad = int(words[1])
                    if rad < 0:
                        rad = 1
                    elif rad > 100:
                        rad = 100
                except BaseException:
                    rad = 1
            try:
                amount = int(words[0])
                if amount > 20000000:
                    amount = 20000000
                elif amount < -20000000:
                    amount = -20000000
            except BaseException:
                amount = 5000
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
            with Image.open(photo_download.raw) as photo:
                photo = photo.filter(
                    ImageFilter.UnsharpMask(
                        percent=amount,
                        radius=rad,
                        threshold=1))
                photo.save(result, format='PNG')
            result.seek(0)
            response = upload.photo_messages(result)[0]
            vk.messages.send(
                peer_id=event.peer_id,
                message='[id{2}|Твое] фото (amount = {0}, radius = {1}):'.format(
                    amount, rad, event.user_id),
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
