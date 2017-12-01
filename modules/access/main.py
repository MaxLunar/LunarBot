import json

documentation = """access - установка и просмотр прав пользователей.
Использование: access set/get user_id"""
access = 'superadmin'

def call(**kw):
    vk = kw['vk']
    event = kw['event']
    bot = kw['bot']
    try:
        msg = list(filter(None, event.text.split()))
        msg.pop(0)
        msg.pop(0)
        if event:
            action = msg.pop(0)
            
            if msg:
                access = bot.config['access']
                if action == 'get':
                    user = 'user'
                    user_id = int(''.join(filter(lambda x: x.isdigit(), msg.pop(0))))
                    for level in access:
                        if user_id in access[level]:
                            user = level
                            break
                    vk.messages.send(
                            peer_id=event.peer_id,
                            message='Уровень доступа: <{0}>.'.format(user),
                            forward_messages=event.message_id
                            ) 
    except Exception as err:
        print(err)
        return False
