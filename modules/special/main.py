import functools

documentation = """special - [ДАННЫЕ УДАЛЕНЫ]
Использование - L special"""

access = 'user'

def call(**kw):
    vk = kw['vk']
    event = kw['event']
    try:
        spec = str(event.user_id)
        while len(spec) != 1:
            spec = str(functools.reduce(int.__add__, map(int, list(spec))))
        if spec == '7':
            response = '[{0}] Ты - особенный юзер.'.format(spec)
        else:
            response = '[{0}] Ты - обычный юзер.'.format(spec)
        vk.messages.send(
                peer_id=event.peer_id,
                message=response,
                forward_messages=event.message_id
                )
    except Exception as err:
        print(err)
        return False
