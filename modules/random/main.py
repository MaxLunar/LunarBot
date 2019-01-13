import random

max_size = 48

documentation = """random X Y - генерирует случайное число в промежутке [X; Y].
Числа X и Y не должны превышать {0} знаков в длину.""".format(max_size)

access = 'user'


def call(**kw):
    vk = kw['vk']
    event = kw['event']
    try:
        msg = list(filter(None, event.text.split()))
        if len(msg[2]) > max_size or len(msg[3]) > max_size:
            vk.messages.send(
                peer_id=event.peer_id,
                message='Введенные числа слишком большие (это не значит, что бот не может их обработать).',
                random_id=random.randrange(2**32),
                forward_messages=event.message_id
            )
            return None
        num1, num2 = int(msg[2]), int(msg[3])
        if num1 < num2:
            response = 'Твое число: {0}.'.format(random.randint(num1, num2))
        elif num1 > num2:
            response = 'Твое число: {0}.'.format(random.randint(num2, num1))
        elif num1 == num2:
            response = 'Твое число: {0}\n(сверхразум detected).'.format(num1)
        vk.messages.send(
            peer_id=event.peer_id,
            message=response,
            random_id=random.randrange(2**32),
            forward_messages=event.message_id
        )
    except Exception as err:
        print(err)
        return False
