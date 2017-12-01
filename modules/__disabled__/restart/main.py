import os
import sys
from subprocess import check_output

documentation = """restart - перезапуск бота."""
access = 'superadmin'

def handle():
    with open(sys.path[])
    os.system('python3 /home/maxlunar/bot-dev/bot.py')

def call(**kw):
    vk = kw['vk']
    event = kw['event']
    bot = kw['bot']
    try:
        if event.user_id in bot.access[access]:
            vk.messages.send(
                    peer_id=event.peer_id,
                    message='Выполняется перезапуск бота.',
                    forward_messages=event.message_id
                    )
            sys.exit()

    except Exception as err:
        print(err)
        return False
