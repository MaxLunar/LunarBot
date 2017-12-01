import hashlib

hash_list = {
        'sha1': lambda string: hashlib.sha1(string.encode('utf-8')).hexdigest(),
        'sha224': lambda string: hashlib.sha224(string.encode('utf-8')).hexdigest(),
        'sha256': lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest(),
        'sha384': lambda string: hashlib.sha384(string.encode('utf-8')).hexdigest(),
        'sha512': lambda string: hashlib.sha512(string.encode('utf-8')).hexdigest(),
        'md5': lambda string: hashlib.md5(string.encode('utf-8')).hexdigest()
        }

documentation = """crypto - различные хеши и шифрования
Доступные хеши - {0}.
Использование - L crypto sha256 *ваш_текст*""".format(', '.join(hash_list.keys()))
access = 'user'

def call(**kw):
    vk = kw['vk']
    event = kw['event']
    try:
        msg = event.text.split()
        hashtype = msg[2:][0]
        text = ' '.join(msg[3:])
        if hashtype in hash_list.keys():
            vk.messages.send(
                    peer_id=event.peer_id,
                    message='Результат: {0}'.format(hash_list[hashtype](text)),
                    forward_messages=event.message_id
                    )
    except Exception as err:
        print(err)
        return False
