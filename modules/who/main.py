import re
import random

documentation = """who - выбирает случайного пользователя из беседы"""

access = 'user'


def call(**kw):
    vk = kw['vk']
    event = kw['event']
    bot = kw['bot']
    try:
        if event.from_chat:
            users = vk.messages.getChatUsers(chat_id=event.chat_id)
            user = vk.users.get(user_id=random.choice(users))[0]
            vk.messages.send(
                peer_id=event.peer_id,
                message='{0} {1}.'.format(
                    user['first_name'], user['last_name']),
                random_id=random.randrange(2**32),
                forward_messages=event.message_id
            )
    except Exception as err:
        print(err)
        return False
