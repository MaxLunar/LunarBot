import re
import random
import traceback

documentation = """roll - бросает кости в формате XdY"""

access = 'user'


def call(**kw):
    vk = kw['vk']
    event = kw['event']
    bot = kw['bot']
    try:
        msg = list(filter(None, event.text.split()))[2:]
        if msg:
            pattern = re.compile('[0-9]+d[0-9]+')
            dice = pattern.findall(
                ' '.join(msg).replace(
                    'д',
                    'd').replace(
                    'Д',
                    'd').replace(
                    'D',
                    'd'))
            correct = []
            for item in dice:
                d = list(map(int, item.split('d')))
                if d[0] in range(1, 51) and d[1] in range(
                        1, 1001) and len(correct) <= 5:
                    correct.append(d)
            if not correct:
                return False
            template = 'Кость {0}: {1}d{2}\nБроски: ({3}) => {4}\n\n'
            response = ''
            for num, item in enumerate(correct, 1):
                rolls = []
                for i in range(item[0]):
                    rolls.append(str(random.randint(1, item[1])))
                response = response + \
                    template.format(num, *
                                    item, '|'.join(rolls), sum(map(int, rolls)))
            vk.messages.send(
                peer_id=event.peer_id,
                message=response,
                random_id=random.randrange(2**32),
                forward_messages=event.message_id
            )
    except Exception as err:
        vk.messages.send(
            peer_id=event.peer_id,
            message='[ERROR]\n{0}'.format(traceback.format_exc()),
            random_id=random.randrange(2**32),
            forward_messages=event.message_id
        )
        return False
