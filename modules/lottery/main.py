import shelve
import random
import functools

mult_list = (2, 3, 4)

def_mult = mult_list[0]

cfg = '/'.join(__file__.split('/')[:-1])+'/balance'

db = shelve.open(cfg, 'c', writeback=True)


documentation = """lottery - лотерея на виртуальные деревянные.
Использование (узнать счет) - L lottery
(обычное вращение, multiplier - множитель денег, по дефолту {0}, может быть следующим {1}) - L lottery <money> [multiplier])""".format(def_mult, mult_list)

access = 'user'

def terminate():
    db.close()

def call(**kw):
    vk = kw['vk']
    event = kw['event']
    try:
        msg = list(filter(None, event.text.split()))
        msg.pop(0)
        msg.pop(0)
        response = None
        user = str(event.user_id)
        if db.get(user):
            user_bal = db[user]
        else:
            db[user] = 100
            user_bal = 100
        if msg:
            if msg[0].isdigit():
                bet = int(msg.pop(0))
                if msg and bet:
                    mult = int(msg.pop(0))
                    if mult in mult_list:
                        pass
                    else:
                        mult = 2
                    
                    if bet > user_bal:
                        response = 'Слишком большая сумма.'
                    else:
                        drop = random.choice(range(1, mult+1))
                        value = bet*(mult-1)
                        if drop == mult:
                            db[user] += value
                            response = 'Вы выиграли (+{0}$).\nТекущий баланс: {1}$.'.format(value, db[user])
                        else:
                            db[user] -= value
                            if db[user] < 0:
                                db[user] = 0
                            response = 'Вы проиграли (-{0}$).\nТекущий баланс: {1}$.'.format(value, db[user])
                    
                else:
                    mult = 2
            else:
                response = '[ERROR]\nВаш баланс: {0}$.'.format(user_bal)
        else:
            response = 'Ваш баланс: {0}$.'.format(user_bal)
        if response:
            vk.messages.send(
                    peer_id=event.peer_id,
                    message=response,
                    forward_messages=event.message_id
                    )
    except Exception as err:
        return False
