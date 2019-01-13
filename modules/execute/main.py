# -*- coding: utf-8 -*-
import io
import random
import html
import traceback
from contextlib import redirect_stdout

import vk_api
from vk_api.audio import VkAudio

documentation = """execute - выполняет Python команду.
Использование - L execute print("kek")"""

access = 'superadmin'


class MyGlobals(dict):
    def __init__(self, globs, locs):
        self.globals = globs
        self.locals = locs

    def __getitem__(self, name):
        try:
            return self.locals[name]
        except KeyError:
            return self.globals[name]

    def __setitem__(self, name, value):
        self.globals[name] = value

    def __delitem__(self, name):
        del self.globals[name]


def call(**kw):
    vk = kw['vk']
    vk_session = kw['vk_session']
    event = kw['event']
    bot = kw['bot']
    audio = VkAudio(vk_session)
    try:
        driver = kw['bot'].utilities['webdriver']
    except BaseException:
        pass
    try:
        msg = event.text.split(' ')[2:]  # default split eats newlines
        command = html.unescape(' '.join(msg))
        command = command.replace(chr(0x1f31a), '    ')
        out = io.StringIO()
        d = MyGlobals(globals(), locals())
        with redirect_stdout(out):
            exec(command, d)
        vk.messages.send(
            peer_id=event.peer_id,
            message=out.getvalue(),
            random_id=random.randrange(2**32),
            forward_messages=event.message_id
        )
    except Exception as err:
        vk.messages.send(
            peer_id=event.peer_id,
            message='[ERROR]\n{0}'.format(traceback.format_exc()),
            random_id=random.randrange(2**32),
            forward_messages=event.message_id
        )
        return False
