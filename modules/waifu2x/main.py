# -*- coding: utf-8 -*-
import io
import random
import vk_api
import requests
import traceback

from bs4 import BeautifulSoup

documentation = """waifu2x - увеличивает пикчу в 2 раза без потери качества"""

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
            response = requests.get(
                'https://waifu2x.booru.pics/Home/fromlink',
                params={
                    'denoise': 1,
                    'scale': 2,
                    'url': photo_url})

            img_link = response.url
            '''
            soup = BeautifulSoup(response.text)
            img_link = None
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    if href.endswith('.png'):
                        img_link = 'https://waifu2x.booru.pics'+href
            '''
            if img_link:
                vk.messages.send(
                    peer_id=event.peer_id,
                    message='[id{0}|Твое] фото: {1}'.format(
                        event.user_id, img_link),
                    random_id=random.randrange(2**32),
                )
            else:
                vk.messages.send(
                    peer_id=event.peer_id,
                    message='Возможно фото слишком большое / неизвестная ошибка.',
                    random_id=random.randrange(2**32),
                )

    except Exception as err:
        vk.messages.send(
            peer_id=event.peer_id,
            message='[ERROR]\n{0}'.format(traceback.format_exc()),
            random_id=random.randrange(2**32),
            forward_messages=event.message_id
        )
        return False
