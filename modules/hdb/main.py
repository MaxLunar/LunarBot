import random
import traceback
import requests

documentation = """hdb - проверить хеш SHA256/SHA1/MD5 на совпадение. Использование - hdb [sha256/md5/sha1] hash"""

access = 'user'


def call(**kw):
    vk = kw['vk']
    event = kw['event']
    try:
        msg = list(filter(None, event.text.lower().split()))[2:]
        if msg[0] in ('sha256', 'md5', 'sha1') and len(msg) >= 2:
            response = requests.get(
                'https://hashdb.insomnia247.nl/v1/{0}/{1}'.format(msg[0], msg[1]))
            jres = response.json()
            vk.messages.send(
                peer_id=event.peer_id,
                message='Найден: {1}\nРезультат: {2}'.format(
                    jres['hash'], jres['found'], jres['result']),
                random_id=random.randrange(2**32),
                forward_messages=event.message_id
            )
            return True
    except Exception as err:
        print(err)
        # vk.messages.send(
        #            peer_id=event.peer_id,
        #            message='[ERROR]\n{0}'.format(traceback.format_exc()),
        #            forward_messages=event.message_id
        #            )
        return False
