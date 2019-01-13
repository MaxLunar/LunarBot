# -*- coding: utf-8 -*-
import io
import random
import vk_api
import requests
import traceback
import zlib

from random import choice, randint
from PIL import Image

documentation = """pngsplice - смешивает 2 пикчи в процентном соотношении в PNG-glitch стиле"""

access = 'user'


class PNGChunk:
    def __init__(self, dat):
        self._raw = dat
        self._length = self._raw[:4]
        self.length = int.from_bytes(self._length, byteorder='big')
        self.type = self._raw[4:8]
        self.data = self._raw[8:-4]
        self.crc = self._raw[-4:]
        #assert self.crc == PNGChunk.crc32(self.type+self.data)

    def __repr__(self):
        return '<{} \'{}\'>'.format(
            self.__class__.__name__, self.type.decode('ascii'))

    def update_data(self, dat):
        self.data = dat
        self.length = len(dat)
        self._length = bytes.fromhex(hex(self.length)[2:].zfill(8))
        self.crc = PNGChunk.crc32(self.type + self.data)
        self._raw = self._length + self.type + self.data + self.crc

    @staticmethod
    def parse_data(dat):
        for ch in range(len(dat)):
            if dat[ch:ch + 4] in [b'IHDR', b'IDAT', b'IEND']:
                length = int.from_bytes(dat[ch - 4:ch], byteorder='big')
                yield PNGChunk(dat[ch - 4:ch + 8 + length])

    @staticmethod
    def crc32(dat):
        return bytes.fromhex(hex(zlib.crc32(dat) & 0xffffffff)[2:].zfill(8))

    @staticmethod
    def join_idat(seq):
        length = 0
        type = b'IDAT'
        data = bytes()
        for chunk in seq:
            if chunk.type == type:
                length += chunk.length
                data += chunk.data
        return PNGChunk(bytes.fromhex(hex(length)[2:].zfill(
            8)) + type + data + PNGChunk.crc32(type + data))


def call(**kw):
    vk = kw['vk']
    event = kw['event']
    vk_session = kw['vk_session']
    try:
        upload = vk_api.VkUpload(vk_session)
        msg = vk.messages.getById(message_ids=[event.message_id])['items'][0]
        message = list(filter(None, event.text.split()))[2:]
        try:
            percent = int(message[0])
            if percent not in range(101):
                percent = 50
        except BaseException:
            percent = 50
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
            photo_1 = io.BytesIO(photo_download_1.content)
            photo_2 = io.BytesIO(photo_download_2.content)

            data_1 = Image.open(photo_1)
            data_2 = Image.open(photo_2)
            data_2 = data_2.resize(data_1.size)

            data_1.save(photo_1, format='PNG')
            data_2.save(photo_2, format='PNG')

            photo_1.seek(0)
            photo_2.seek(0)

            chunks = list(PNGChunk.parse_data(photo_1.read()))
            chunks[1:-1] = [PNGChunk.join_idat(chunks)]
            chunks_aux = list(PNGChunk.parse_data(photo_2.read()))
            chunks_aux[1:-1] = [PNGChunk.join_idat(chunks_aux)]

            data = zlib.decompress(chunks[1].data)
            data_aux = zlib.decompress(chunks_aux[1].data)

            data = bytes(list(v)[randint(0, 100) < percent]
                         for v in zip(data, data_aux))

            chunks[1].update_data(zlib.compress(data))

            signature = b'\x89PNG\r\n\x1a\n'
            for chunk in chunks:
                signature += chunk._raw
            result = io.BytesIO(signature)

            response = upload.photo_messages(result)[0]
            vk.messages.send(
                peer_id=event.peer_id,
                message='[id{0}|Твое] фото (percentage = {1}%):'.format(
                    event.user_id, percent),
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
