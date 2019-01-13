# -*- coding: utf-8 -*-
import io
import random
import vk_api
import requests
import traceback

from PIL import Image

documentation = """bandremap - перемешивает каналы пикчи из RGB в любую комбинацию."""

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
                    photo_url = list(sorted(
                        attach['photo']['sizes'], key=lambda x: x['height'] + x['width']))[-1]['url']
                    break
        if photo_url is not None:
            photo_download = requests.get(photo_url, stream=True)
            photo_download.raw.decode_content = True
            result = io.BytesIO()
            with Image.open(photo_download.raw) as photo:
                bands_str = None
                if len(message) > 2:
                    if message[2].isalpha() and len(message[2]) == 3:
                        bands_str = message[2].upper()
                        for l in bands_str:
                            if l not in 'RGB':
                                bands_str = None
                                break
                bands_list = []
                if bands_str:
                    for x in bands_str:
                        if x is 'R':
                            bands_list.append(0)
                        elif x is 'G':
                            bands_list.append(1)
                        elif x is 'B':
                            bands_list.append(2)
                if len(bands_list) != 3:
                    return
                band_split = photo.convert('RGB').split()
                photo = Image.merge(
                    mode='RGB', bands=[
                        band_split[b] for b in bands_list])
                photo.save(result, format='PNG')
                result.seek(0)
            response = upload.photo_messages(result)[0]
            vk.messages.send(
                peer_id=event.peer_id,
                message='[id{1}|Твое] фото (RGB -> {0}):'.format(
                    message[2].upper(), event.user_id),
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
