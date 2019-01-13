# -*- coding: utf-8 -*-
import io
import random
import re
import vk_api
import requests
import traceback
from wand.image import Image

documentation = """dmeme - двойные мемы из 2 пикч"""

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

            img1 = io.BytesIO()
            img2 = io.BytesIO()
            img1copy = io.BytesIO()

            im1_size = None
            im2_size = None
            with Image(file=photo_download_1.raw) as photo1, Image(file=photo_download_2.raw) as photo2:
                photo1.transform(resize='604x604>')
                photo1.transform(resize='604x604<')
                photo2.transform(resize='1280x1024>')
                photo2.transform(resize='1280x1024<')
                # for dim in range(2):
                #    if photo2.size[dim] == max(photo2.size):
                #        if photo2.size[dim] <= 1024:
                #            if dim == 0:
                #                photo2.transform(resize='1280x')
                #            elif dim == 1:
                #                photo2.transform(resize='x1280')
                im1_size = photo1.size
                im2_size = photo2.size
                photo1.save(file=img1)
                photo2.save(file=img2)

            img1.seek(0)
            img2.seek(0)
            img1copy.write(img1.read())
            img1.seek(0)
            img1copy.seek(0)

            img1.name = 'img.png'
            img2.name = 'img.png'
            img1copy.name = 'img.png'

            response = upload.photo_messages(img1copy)[0]
            photo_id = '{0}_{1}'.format(response['owner_id'], response['id'])

            editor = vk_session.http.post(
                'https://vk.com/al_photos.php',
                params={
                    'act': 'edit_photo',
                    'al': '1',
                    'photo': photo_id
                }
            ).text

            updater = {
                'act': 'save_desc',
                'al': 1,
                'conf': '///',
                'cover': '',
                'filter_num': 0,
                'text': '',
                'photo': photo_id,
            }

            updater['upload_url'] = re.search(
                '(?<="upload_url":")([^"]*)',
                editor).group().replace(
                '\\',
                '')
            updater['hash'] = re.search('([a-f0-9]{18})', editor).group()
            updater['aid'] = re.search(
                r'(?<=selectedItems: \[)([^\]]+)', editor).group()

            updater['_query'] = vk_session.http.post(
                updater['upload_url'],
                files={'photo': img2}
            ).text

            vk_session.http.post(
                'https://vk.com/al_photos.php',
                params=updater
            )

            updater['_query'] = vk_session.http.post(
                updater['upload_url'],
                files={'photo': img1}
            ).text

            vk_session.http.post(
                'https://vk.com/al_photos.php',
                params=updater
            )

            vk.photos.delete(
                owner_id=response['owner_id'],
                photo_id=response['id']
            )

            vk.photos.restore(
                owner_id=response['owner_id'],
                photo_id=response['id']
            )

            attach_id = 'photo{0}_{1}'.format(
                response['owner_id'], response['id'])
            vk.messages.send(
                peer_id=event.peer_id,
                message='[id{0}|Твое] фото (im1 = {1}, im2 = {2}):'.format(
                    event.user_id, im1_size, im2_size),
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
