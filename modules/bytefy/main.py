import io
import random
import vk_api
import requests
import traceback

from random import randint
from PIL import Image

documentation = """bytefy - выжигает пиксели пикчи по множителю"""

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
                data = list(photo.tobytes())
                target = None
                if len(message) > 2:
                    if message[2].isdigit():
                        if int(message[2]) in range(2, 128 + 1):
                            target = int(message[2])
                if not target:
                    target = randint(2, 24)
                data[::] = map(lambda a: a * target, data[::])

                divider = 1
                total_samples = 0
                sample_count = 'NULL'
                while sample_count:
                    sample_count = 0
                    for i in range(len(data)):
                        if data[i] > 255:
                            sample_count += 1
                            old = data[i]
                            data[i] = old % 256
                            if i + 1 < len(data):
                                data[i + 1] += round((old - old %
                                                      256) / divider)
                    total_samples += sample_count

                data = bytes(data)

                img = Image.frombytes(
                    data=data, size=photo.size, mode=photo.mode)
                img.save(result, format='PNG')
                result.seek(0)
            response = upload.photo_messages(result)[0]
            vk.messages.send(
                peer_id=event.peer_id,
                message='[id{2}|Твое] фото (mult = {0}; total samples = {1}):'.format(
                    target, total_samples, event.user_id),
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
