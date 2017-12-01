import random

documentation = """who - выбирает случайного пользователя из беседы"""

access = 'user'

def call(**kw):
    vk = kw['vk']
    event = kw['event']
    bot = kw['bot']
    try:
        if event.from_chat:
            msg_ = event.text.split()[2:]
            msg = ' '.join(msg_)
            users = vk.messages.getChatUsers(chat_id=event.chat_id)
            user = vk.users.get(user_id=random.choice(users))[0]
            if msg_:
                vk.messages.send(
                        peer_id=event.peer_id,
                        message='{0} {1} - {2}.'.format(user['first_name'], user['last_name'], msg),
                        forward_messages=event.message_id
                        )
            else:
                vk.messages.send(
                        peer_id=event.peer_id,
                        message='{0} {1}.'.format(user['first_name'], user['last_name']),
                        forward_messages=event.message_id
                        )
    except Exception as err:
        print(err)
        return False
