import json

documentation = """config - обновление/установка конфигурации бота (сырой интерфейс).
Использование: config set/get [field:subfield] [value]
Установка и получение персональных данных невозможны по причинам безопасности."""
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
            
            if action == 'get':
                cfg = bot.config
                cfg.pop('login')
                cfg.pop('password')
                if not msg:
                    vk.messages.send(
                            peer_id=event.peer_id,
                            message='Файл конфигурации:\n'+json.dumps(cfg),
                            forward_messages=event.message_id
                            ) 
    except Exception as err:
        print(err)
        return False
