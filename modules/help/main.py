import random

documentation = None
access = 'user'


def call(**kw):
    vk = kw['vk']
    event = kw['event']
    bot = kw['bot']
    try:
        if bot.sources:
            access = 'user'
            for level in bot.access.keys():
                if event.user_id in bot.access[level]:
                    access = level
                    break

            wrapper = '=' * 20 + \
                '\nLunarbot\nВключенные и доступные для вас команды:\n==========\n{0}\n'
            body = '{0}\n==========\n'
            for module in bot.sources.keys():
                if bot.sources[module].documentation and bot.sources[module].access >= access:
                    wrapper = wrapper.format(body.format(
                        bot.sources[module].documentation) + '{0}')
            wrapper = wrapper.format('')
            vk.messages.send(
                peer_id=event.peer_id,
                message=wrapper,
                random_id=random.randrange(2**32),
                forward_messages=event.message_id
            )
    except Exception as err:
        print(err)
        return False
