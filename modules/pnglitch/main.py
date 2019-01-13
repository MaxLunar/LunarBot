# -*- coding: utf-8 -*-
import io
import random
import vk_api
import requests
import traceback
import zlib

from random import choice
from PIL import Image

documentation = """pnglitch - разьебывает пикчу PNG-глитчами"""

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
        param = choice(range(256))
        target = choice(range(256))
        if message:
            try:
                param = int(message[0])
                if param not in range(256):
                    param = choice(range(256))
            except BaseException:
                param = choice(range(256))

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
            photo = io.BytesIO(photo_download.content)
            data = Image.open(photo)
            data.save(photo, format='PNG')
            photo.seek(0)
            chunks = list(PNGChunk.parse_data(photo.read()))
            chunks[1:-1] = [PNGChunk.join_idat(chunks)]
            data = zlib.decompress(chunks[1].data)
            data = data.replace(bytes([param]), bytes([target]))
            chunks[1].update_data(zlib.compress(data))

            signature = b'\x89PNG\r\n\x1a\n'
            for chunk in chunks:
                signature += chunk._raw
            result = io.BytesIO(signature)

            response = upload.photo_messages(result)[0]
            vk.messages.send(
                peer_id=event.peer_id,
                message='[id{0}|Твое] фото (param = {1}, target = {2}):'.format(
                    event.user_id, repr(bytes([param])), repr(bytes([target]))),
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
