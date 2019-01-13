# -*- coding: utf-8 -*-
import io
import random
import colour
import vk_api
import traceback
from PIL import Image, ImageDraw, ImageOps

documentation = """strip - генерит рандомные полоски"""

access = 'user'


def gen_bounds(size, amount, orientation='v'):
    if orientation == 'h':
        o = -1
    else:
        o = 1
    size = size[::o]
    if orientation == 'd':
        for x in range(amount * 2)[::2]:
            yield [(round((size[0] / amount) * x), 0)[::o],
                   (0, round((size[1] / amount) * x))[::o],
                   (round((size[0] / amount) * (x + 1)), 0)[::-o],
                   (0, round((size[1] / amount) * (x + 1)))[::-o]]
    elif orientation == 'c':
        center = (size[0] // 2, size[1] // 2)
        for x in range(amount * 6)[1::2]:
            yield [(center[0] - round(center[0] / amount) * x,
                    center[1] - round(center[1] / amount) * x),
                   (center[0] + round(center[0] / amount) * x,
                    center[1] + round(center[1] / amount) * x)]
    else:
        for x in range(amount)[::2]:
            yield [(round((size[0] / amount) * x), 0)[::o],
                   (round((size[0] / amount) * (x + 1)), size[1])[::o]]


def call(**kw):
    vk = kw['vk']
    event = kw['event']
    vk_session = kw['vk_session']
    try:
        upload = vk_api.VkUpload(vk_session)
        msg = None  # placeholder TODO choosing parameters
        first_color = colour.Color(
            rgb=tuple(
                random.randint(
                    0,
                    255) /
                255 for _ in range(3)))
        first = tuple(int(x * 255) for x in first_color.rgb)

        second_color = colour.Color(
            rgb=tuple(
                random.randint(
                    0,
                    255) /
                255 for _ in range(3)))
        second = tuple(int(x * 255) for x in second_color.rgb)

        ssize = 2000

        img = Image.new(mode='RGB', size=(ssize, ssize), color=first)
        draw = ImageDraw.ImageDraw(img)

        orient = random.choice('vhdc')
        mirroring = 'n'
        if orient == 'd':
            mirroring = random.choice('nhv')
        strips = tuple(gen_bounds(img.size, random.randint(5, 29), orient))
        if orient == 'd':
            for bound in strips:
                draw.polygon(bound, second)
        elif orient == 'c':
            edge = random.choice('nabcd')
            ticker = True
            for bound in strips[::-1]:
                ticker = not ticker
                coord = bound
                if edge == 'a':
                    coord = tuple(
                        (lambda p: (
                            p[0] -
                            ssize //
                            2,
                            p[1] -
                            ssize //
                            2))(z) for z in coord)
                elif edge == 'b':
                    coord = tuple(
                        (lambda p: (
                            p[0] +
                            ssize //
                            2,
                            p[1] -
                            ssize //
                            2))(z) for z in coord)
                elif edge == 'c':
                    coord = tuple(
                        (lambda p: (
                            p[0] -
                            ssize //
                            2,
                            p[1] +
                            ssize //
                            2))(z) for z in coord)
                elif edge == 'd':
                    coord = tuple(
                        (lambda p: (
                            p[0] +
                            ssize //
                            2,
                            p[1] +
                            ssize //
                            2))(z) for z in coord)
                if ticker:
                    draw.ellipse(coord, second)
                else:
                    draw.ellipse(coord, first)
        else:
            for bound in strips:
                draw.rectangle(bound, second)

        if orient == 'd':
            if random.choice(range(2)):
                img = img.rotate(90)

        if mirroring == 'h':
            img_half = img.crop((0, 0, img.width // 2, img.height))
            img_flip = ImageOps.mirror(img_half)
            img.paste(img_flip, (img.width // 2, 0))
        elif mirroring == 'v':
            img_half = img.crop((0, 0, img.width, img.height // 2))
            img_flip = ImageOps.flip(img_half)
            img.paste(img_flip, (0, img.height // 2))

        result = io.BytesIO()
        img.save(result, format='PNG')
        result.seek(0)
        response = upload.photo_messages(result)[0]
        vk.messages.send(
            peer_id=event.peer_id,
            message='[id{0}|Твое] фото ({1} - {2}):'.format(
                event.user_id, first_color.hex_l.upper(), second_color.hex_l.upper()),
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
