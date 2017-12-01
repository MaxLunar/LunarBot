documentation = """status - Позволяет узнать свой уровень допуска к командам бота.
Некоторые команды не доступны обычным пользователям по тем или иным причинам."""
access = 'user'
def call(**kw):
    vk = kw['vk']
    event = kw['event']
    bot = kw['bot']
    try:
        for level in bot.access.keys():
            if event.user_id in bot.access[level]:
                vk.messages.send(
                        peer_id=event.peer_id,
                        message='Ваш уровень допуска: <{0}>.'.format(level),
                        forward_messages=event.message_id
                        )
                break
        else:
            vk.messages.send(
                    peer_id=event.peer_id,
                    message='Ваш уровень допуска: <user>.',
                    forward_messages=event.message_id
                    )
    except Exception as err:
        print(err)
        return False
