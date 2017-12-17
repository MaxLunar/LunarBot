# -*- coding: utf-8 -*-
import io
import html
import traceback
from contextlib import redirect_stdout

documentation = """execute - выполняет Python команду.
Использование - L execute print("kek")"""

access = 'superadmin'
def call(**kw):
    vk = kw['vk']
    event = kw['event']
    try:
        msg = event.text.split()[2:]
        command = html.unescape(' '.join(msg))
        out = io.StringIO()

        with redirect_stdout(out):
            exec(command)
        vk.messages.send(
                peer_id=event.peer_id,
                message=out.getvalue(),
                forward_messages=event.message_id
                )
    except Exception as err:
        vk.messages.send(
                peer_id=event.peer_id,
                message='[ERROR]\n{0}'.format(traceback.format_exc()),
                forward_messages=event.message_id
                )
        return False
