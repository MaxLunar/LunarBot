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
                acc = bot.config['access']
                if action == 'get':
                    lvl = 'user'
                    user = int(msg.pop(0))
                    first_name, last_name = None, None
                    try:
                        info = vk.users.get(user_id=user)[0]
                        first_name = info['first_name']
                        last_name = info['last_name']
                    except:
                        return False
                    for level in acc.keys():
                        if user in acc[level]:
                            lvl = level
                            break
                    vk.messages.send(
                            peer_id=event.peer_id,
                            message='Уровень доступа пользователя {2} {3} (id{1}): <{0}>.'.format(lvl, user, first_name, last_name),
                            forward_messages=event.message_id
                            )
                if action == 'set' and msg:
                    user = int(msg.pop(0))
                    level = msg.pop(0)
                    first_name, last_name = None, None
                    if level not in acc:
                        if level == 'user':
                            pass
                        else:
                            return False

                    try:
                        info = vk.users.get(user_id=user)[0]
                        first_name = info['first_name']
                        last_name = info['last_name']
                    except:
                        return False

                    if level != 'user':
                        if user in acc[level]:
                            return True

                    for lvl in acc.keys():
                        if user in acc[lvl]:
                            acc[lvl].remove(user)
                            break
                    
                    if level != 'user':
                        acc[level].append(user)
                    
                    bot.write_cfg()
                    vk.messages.send(
                            peer_id=event.peer_id,
                            message='Пользователю {2} {3} (id{0}) был установлен уровень доступа <{1}>.'.format(user, level, first_name, last_name),
                            forward_messages=event.message_id
                            )
    except Exception as err:
        print(err)
        return False
