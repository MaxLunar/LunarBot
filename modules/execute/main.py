# -*- coding: utf-8 -*-
import io
import html
import traceback
from contextlib import redirect_stdout

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
    event = kw['event']
    driver = kw['bot'].utilities['webdriver']
    try:
        msg = event.text.split()[2:]
        command = html.unescape(' '.join(msg))
        out = io.StringIO()
        d = MyGlobals(globals(), locals())
        with redirect_stdout(out):
            exec(command, d)
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
