# -*- coding: utf-8 -*-
import io
import os
import vk_api
import requests
import traceback
import sox
import tempfile

documentation = """reverse - переворачивает аудио задом наперед"""

access = 'user'


def call(**kw):
    vk = kw['vk']
    event = kw['event']
    vk_session = kw['vk_session']
    try:
        upload = vk_api.VkUpload(vk_session)
        msg = vk.messages.getById(message_ids=[event.message_id])['items'][0]
        audio_url = None
        audio_artist = None
        audio_title = None
        audio_duration = None
        attachments = msg.get('attachments', None)
        if attachments is not None:
            for attach in attachments:
                if attach['type'] == 'audio':
                    audio_url = attach['audio']['url']
                    audio_artist = attach['audio']['artist']
                    audio_title = attach['audio']['title']
                    audio_duration = attach['audio']['duration']

                    break
        if not audio_url:
            vk.messages.send(
                peer_id=event.peer_id,
                message='ВК не отдал ссылку на аудио.',
                forward_messages=event.message_id
            )
            return False
        if audio_duration > 600:
            vk.messages.send(
                peer_id=event.peer_id,
                message='Длина аудио больше 10 минут.',
                forward_messages=event.message_id
            )
            return False

        if audio_url is not None:
            audio_download = requests.get(audio_url, stream=True)
            audio_download.raw.decode_content = True
            result = None
            with tempfile.NamedTemporaryFile(suffix='.mp3', dir='/dev/shm/', delete=False) as input_file, tempfile.NamedTemporaryFile(suffix='.mp3', dir='/dev/shm/', delete=False) as output_file:
                input_file.write(audio_download.content)
                in_name = input_file.name
                out_name = output_file.name
                tfm = sox.Transformer()
                tfm = tfm.reverse()
                # input_file.close()
                # output_file.close()
                r = tfm.build(in_name, out_name, return_output=True)
                output_file = open(out_name, 'rb')
                result = io.BytesIO(output_file.read())
                output_file.close()
                os.unlink(in_name)
                os.unlink(out_name)
                result.name = 'file.mp3'
                result.seek(0)

            response = upload.audio(
                result, 'lunarbot', '{0} - {1} | reversed by lunarbot'.format(audio_artist, audio_title))
            vk.messages.send(
                peer_id=event.peer_id,
                message='[id{0}|Твое] аудио:'.format(event.user_id),
                attachment='audio{0}_{1}'.format(
                    response['owner_id'], response['id'])
            )

    except Exception as err:
        vk.messages.send(
            peer_id=event.peer_id,
            message='[ERROR]\n{0}'.format(traceback.format_exc()),
            forward_messages=event.message_id
        )
        return False
